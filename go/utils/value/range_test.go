// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"iter"
	"sync"
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"go.chromium.org/turboci/proto/go/utils/ids"
)

var (
	valueRefDesc  = ((*orchestratorpb.ValueRef)(nil)).ProtoReflect().Descriptor()
	hasRefCacheMu sync.Mutex
	hasRefCache   = make(map[protoreflect.Descriptor]bool, 50)
)

func fieldMessageDesc(fd protoreflect.FieldDescriptor) protoreflect.MessageDescriptor {
	if fd.IsMap() {
		return fd.MapValue().Message()
	}
	return fd.Message()
}

// hasValueRef reports whether `desc` is or transitively contains a ValueRef.
func hasValueRef(desc protoreflect.MessageDescriptor) bool {
	hasRefCacheMu.Lock()
	defer hasRefCacheMu.Unlock()
	return hasValueRefLocked(desc)
}

func hasValueRefLocked(desc protoreflect.MessageDescriptor) bool {
	if desc == nil {
		return false
	}
	if desc == valueRefDesc {
		return true
	}

	if hasRef, explored := hasRefCache[desc]; explored {
		return hasRef
	}
	hasRefCache[desc] = false

	fields := desc.Fields()
	for i := range fields.Len() {
		if hasValueRefLocked(fieldMessageDesc(fields.Get(i))) {
			hasRefCache[desc] = true
			return true
		}
	}

	return false
}

// populateAllValueRefs populates one example of every ValueRef reachable from
// `msg`, returning the number of ValueRefs it wrote.
func populateAllValueRefs(msg proto.Message) int {
	return populateRef(msg.ProtoReflect())
}

func populateRef(msg protoreflect.Message) (numRefs int) {
	if msg.Descriptor() == valueRefDesc {
		proto.Merge(msg.Interface(), orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Struct]()),
			Digest:  proto.String("something"),
		}.Build())
		return 1
	}

	fields := msg.Descriptor().Fields()
	for i := range fields.Len() {
		fd := fields.Get(i)
		if !hasValueRef(fieldMessageDesc(fd)) {
			continue
		}
		if od := fd.ContainingOneof(); od != nil && !od.IsSynthetic() {
			active := msg.WhichOneof(od)
			if active == nil {
				panic("oneof " + string(od.FullName()) + " must have an active field set before calling populateAllValueRefs")
			}
			if active != fd {
				continue
			}
		}
		switch {
		case fd.IsList():
			list := msg.Mutable(fd).List()
			if list.Len() == 0 {
				list.AppendMutable()
			}
			for j := range list.Len() {
				numRefs += populateRef(list.Get(j).Message())
			}
		case fd.IsMap():
			key := fd.MapKey().Default().MapKey()
			numRefs += populateRef(msg.Mutable(fd).Map().Mutable(key).Message())
		default:
			numRefs += populateRef(msg.Mutable(fd).Message())
		}
	}
	return numRefs
}

func collectCtxs(seq iter.Seq2[RefContext, *orchestratorpb.ValueRef]) []RefContext {
	var ret []RefContext
	for ctx := range seq {
		ret = append(ret, ctx)
	}
	return ret
}

func commonCtx[Id ids.Identifier](slot orchestratorpb.ValueSlot, id Id) *CommonRefContext {
	return &CommonRefContext{slot: slot, id: ids.Wrap(id)}
}

func resultDataCtx(id *idspb.CheckResult, idx int, actor *orchestratorpb.Actor) *ResultDataRefContext {
	return &ResultDataRefContext{
		CommonRefContext: CommonRefContext{
			slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
			id:   ids.Wrap(id),
		},
		Idx:   idx,
		Actor: actor,
	}
}

// TestRefsInStage ensures that `RefsIn` actually covers all ValueRefs in the
// Stage proto.
//
// If this test fails, it likely means that protobufs for orchestrator.Stage
// have changed and RefsIn needs to be updated.
func TestRefsInStage(t *testing.T) {
	stageID := ids.Stage("S1")
	attemptID := idspb.StageAttempt_builder{Stage: stageID, Idx: proto.Int32(2)}.Build()
	ts := timestamppb.New(time.Unix(100, 0))
	editID := idspb.StageEdit_builder{Stage: stageID, Version: ts}.Build()
	editAttemptID := idspb.StageAttempt_builder{Stage: stageID, Idx: proto.Int32(1)}.Build()
	edit := orchestratorpb.Edit_builder{
		ForNode: ids.Wrap(stageID),
		Version: orchestratorpb.Revision_builder{Ts: ts}.Build(),
		Stage: orchestratorpb.StageDelta_builder{
			Attempts: []*orchestratorpb.StageDelta_Attempt{
				orchestratorpb.StageDelta_Attempt_builder{Identifier: editAttemptID}.Build(),
			},
		}.Build(),
	}.Build()

	stg := orchestratorpb.Stage_builder{
		Identifier: stageID,
		Edits:      []*orchestratorpb.Edit{edit},
		Attempts: []*orchestratorpb.Stage_Attempt{
			orchestratorpb.Stage_Attempt_builder{Identifier: attemptID}.Build(),
		},
	}.Build()
	expect := populateAllValueRefs(stg)

	got := collectCtxs(RefsIn(stg))

	if len(got) != expect {
		t.Fatalf("len(RefsIn(Stage)) = %d, want %d populated ValueRefs", len(got), expect)
	}
	want := []RefContext{
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, stageID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, stageID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL, editID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL, editAttemptID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL, attemptID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL, attemptID),
	}
	if diff := cmp.Diff(want, got, cmp.AllowUnexported(CommonRefContext{}), protocmp.Transform()); diff != "" {
		t.Errorf("RefsIn(Stage) mismatch (-want +got):\n%s", diff)
	}
}

// TestRefsInCheck ensures that `RefsIn` actually covers all ValueRefs in the
// Check proto, traversing Check.results in reverse order.
//
// If this test fails, it likely means that protobufs for orchestrator.Check
// have changed and RefsIn needs to be updated.
func TestRefsInCheck(t *testing.T) {
	checkID := ids.Check("C1")
	res0ID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(1)}.Build()
	res1ID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(2)}.Build()
	editResID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(3)}.Build()
	ts := timestamppb.New(time.Unix(100, 0))
	editID := idspb.CheckEdit_builder{Check: checkID, Version: ts}.Build()
	actor0 := orchestratorpb.Actor_builder{
		WorkplanCreator: &orchestratorpb.Actor_WorkplanCreator{},
	}.Build()
	actor1 := orchestratorpb.Actor_builder{
		Orchestrator: &orchestratorpb.Actor_Orchestrator{},
	}.Build()

	edit := orchestratorpb.Edit_builder{
		ForNode: ids.Wrap(checkID),
		Version: orchestratorpb.Revision_builder{Ts: ts}.Build(),
		Check: orchestratorpb.CheckDelta_builder{
			Results: []*orchestratorpb.CheckDelta_Result{
				orchestratorpb.CheckDelta_Result_builder{Identifier: editResID}.Build(),
			},
		}.Build(),
	}.Build()
	check := orchestratorpb.Check_builder{
		Identifier: checkID,
		Results: []*orchestratorpb.Check_Result{
			orchestratorpb.Check_Result_builder{Identifier: res0ID, Owner: actor0}.Build(),
			orchestratorpb.Check_Result_builder{Identifier: res1ID, Owner: actor1}.Build(),
		},
		Edits: []*orchestratorpb.Edit{edit},
	}.Build()
	expect := populateAllValueRefs(check)

	got := collectCtxs(RefsIn(check))

	if len(got) != expect {
		t.Fatalf("len(RefsIn(Check)) = %d, want %d populated ValueRefs", len(got), expect)
	}
	want := []RefContext{
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, checkID),
		resultDataCtx(res1ID, 1, actor1),
		resultDataCtx(res0ID, 0, actor0),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL, editID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION, editID),
		commonCtx(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA, editResID),
	}
	if diff := cmp.Diff(want, got, cmp.AllowUnexported(CommonRefContext{}), protocmp.Transform()); diff != "" {
		t.Errorf("RefsIn(Check) mismatch (-want +got):\n%s", diff)
	}
}

// TestRefsIn_Counts ensures that `RefsIn` actually covers all ValueRefs in
// Stage, Stage_Attempt, Edit, Check, and WorkPlan protos.
//
// If this test fails, it likely means that orchestrator protobufs have changed
// and RefsIn needs to be updated.
func TestRefsIn_Counts(t *testing.T) {
	stageWithEdit := func() *orchestratorpb.Stage {
		return orchestratorpb.Stage_builder{
			Edits: []*orchestratorpb.Edit{
				orchestratorpb.Edit_builder{
					Stage: &orchestratorpb.StageDelta{},
				}.Build(),
			},
		}.Build()
	}
	checkWithEdit := func() *orchestratorpb.Check {
		return orchestratorpb.Check_builder{
			Edits: []*orchestratorpb.Edit{
				orchestratorpb.Edit_builder{
					Check: &orchestratorpb.CheckDelta{},
				}.Build(),
			},
		}.Build()
	}

	for _, tc := range []struct {
		name string
		msg  proto.Message
	}{
		{
			name: "stage",
			msg:  stageWithEdit(),
		},
		{
			name: "stage_attempt",
			msg:  &orchestratorpb.Stage_Attempt{},
		},
		{
			name: "stage_edit",
			msg: orchestratorpb.Edit_builder{
				Stage: &orchestratorpb.StageDelta{},
			}.Build(),
		},
		{
			name: "check",
			msg:  checkWithEdit(),
		},
		{
			name: "check_edit",
			msg: orchestratorpb.Edit_builder{
				Check: orchestratorpb.CheckDelta_builder{
					State: orchestratorpb.CheckState_CHECK_STATE_FINAL.Enum(),
				}.Build(),
			}.Build(),
		},
		{
			name: "workplan",
			msg: orchestratorpb.WorkPlan_builder{
				Stages: []*orchestratorpb.Stage{stageWithEdit()},
				Checks: []*orchestratorpb.Check{checkWithEdit()},
			}.Build(),
		},
	} {
		t.Run(tc.name, func(t *testing.T) {
			want := populateAllValueRefs(tc.msg)
			if got := len(collectCtxs(RefsIn(tc.msg))); got != want {
				t.Errorf("len(RefsIn(%T)) = %d, want %d", tc.msg, got, want)
			}
		})
	}
}
