// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
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

type NodeType string

const (
	Check NodeType = "Check"
	Stage NodeType = "Stage"
)

var (
	valueRefDesc = ((*orchestratorpb.ValueRef)(nil)).ProtoReflect().Descriptor()
	editDesc     = (*orchestratorpb.Edit)(nil).ProtoReflect().Descriptor()
)

// populateAllValueRefs populates one example of every ValueRef reachable from
// `msg`, returning the number of ValueRefs it wrote.
//
// `nodeType` allows the caller to specify whether `msg` is related to a stage
// or a check, so when working with its Edits we populate only the oneof field
// applicable to that type.
func populateAllValueRefs(msg proto.Message, nodeType NodeType) (numRefs int) {
	// cached helper to tell if we need to walk down a given branch.
	hasRefCache := make(map[protoreflect.Descriptor]bool, 50)
	var hasValueRef func(desc protoreflect.MessageDescriptor) bool
	hasValueRef = func(desc protoreflect.MessageDescriptor) bool {
		if desc == nil {
			return false
		}
		if desc == valueRefDesc {
			return true
		}

		hasRef, explored := hasRefCache[desc]
		if explored {
			return hasRef
		}
		hasRefCache[desc] = false

		fields := desc.Fields()
		for i := range fields.Len() {
			fd := fields.Get(i)
			msg := fd.Message()
			if msg == nil && fd.IsMap() {
				msg = fd.MapValue().Message()
			}
			if msg != nil && (msg == valueRefDesc || hasValueRef(msg)) {
				hasRefCache[desc] = true
				return true
			}
		}

		return false
	}

	// When processing Edit messages, we want to skip the delta field that
	// applies to the other type (skip `check` for stage edits, and `stage`
	// for check edits).
	var editDeltaToSkip string
	if nodeType == Check {
		editDeltaToSkip = "stage"
	} else if nodeType == Stage {
		editDeltaToSkip = "check"
	}

	// Use reflection to generate a skeleton Message with all ValueRef fields set
	// to an instance of a ValueRef without omit reason.
	var skeletonize func(msg protoreflect.Message)
	skeletonize = func(msg protoreflect.Message) {
		if msg.Descriptor() == valueRefDesc {
			proto.Merge(msg.Interface(), orchestratorpb.ValueRef_builder{
				TypeUrl: proto.String(URL[*structpb.Struct]()),
				Digest:  proto.String("something"),
			}.Build())
			numRefs++
			return
		}
		isEdit := msg.Descriptor() == editDesc

		fields := msg.Descriptor().Fields()
		for i := range fields.Len() {
			fd := fields.Get(i)
			if isEdit && fd.Name() == protoreflect.Name(editDeltaToSkip) {
				continue
			}
			if fd.IsList() {
				if hasValueRef(fd.Message()) {
					skeletonize(msg.Mutable(fd).List().AppendMutable().Message())
				}
			} else if fd.IsMap() {
				if hasValueRef(fd.MapValue().Message()) {
					skeletonize(msg.Mutable(fd).Map().Mutable(fd.MapKey().Default().MapKey()).Message())
				}
			} else if hasValueRef(fd.Message()) {
				skeletonize(msg.Mutable(fd).Message())
			}
		}
	}
	skeletonize(msg.ProtoReflect())
	return numRefs
}

// TestRefsInStage ensures that `RefsIn` actually covers all ValueRefs in the
// Stage proto.
//
// If this test fails, it likely means that protobufs for orchestrator.Stage
// have changed and RefsIn needs to be updated.
func TestRefsInStage(t *testing.T) {
	stg := &orchestratorpb.Stage{}
	expect := populateAllValueRefs(stg, Stage)

	stageID := ids.Stage("S1")
	editAttemptID := idspb.StageAttempt_builder{Stage: stageID, Idx: proto.Int32(1)}.Build()
	attemptID := idspb.StageAttempt_builder{Stage: stageID, Idx: proto.Int32(2)}.Build()
	ts := timestamppb.New(time.Unix(100, 0))

	stg.SetIdentifier(stageID)
	stg.GetEdits()[0].SetForNode(ids.Wrap(stageID))
	stg.GetEdits()[0].SetVersion(orchestratorpb.Revision_builder{Ts: ts}.Build())
	stg.GetEdits()[0].GetStage().GetAttempts()[0].SetIdentifier(editAttemptID)
	stg.GetAttempts()[0].SetIdentifier(attemptID)

	var got []RefContext
	for ctx := range RefsIn(stg) {
		got = append(got, ctx)
	}

	if len(got) != expect {
		t.Fatalf("got %d, want %d", len(got), expect)
	}
	want := []RefContext{
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, id: ids.Wrap(stageID)},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, id: ids.Wrap(stageID)},
		&CommonRefContext{
			slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
			id:   ids.Wrap(idspb.StageEdit_builder{Stage: stageID, Version: ts}.Build()),
		},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL, id: ids.Wrap(editAttemptID)},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL, id: ids.Wrap(attemptID)},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL, id: ids.Wrap(attemptID)},
	}
	if diff := cmp.Diff(want, got, cmp.AllowUnexported(CommonRefContext{}), protocmp.Transform()); diff != "" {
		t.Errorf("RefsIn(Stage) mismatch (-want +got):\n%s", diff)
	}
}

// TestRefsInStageAttempt ensures that `RefsIn` actually covers all ValueRefs
// in the Stage Attempt proto.
//
// If this test fails, it likely means that protobufs for
// orchestrator.Stage_Attempt have changed and RefsIn needs to be updated.
func TestRefsInStageAttempt(t *testing.T) {
	atmpt := &orchestratorpb.Stage_Attempt{}
	expect := populateAllValueRefs(atmpt, Stage)

	var found int
	for range RefsIn(atmpt) {
		found++
	}

	if found != expect {
		t.Errorf("got %d, want %d", found, expect)
	}
}

// TestRefsInStageEdit ensures that `RefsIn` actually covers all ValueRefs in
// the Stage Edit proto.
//
// If this test fails, it likely means that protobufs for orchestrator.Edit
// have changed and RefsIn needs to be updated.
func TestRefsInStageEdit(t *testing.T) {
	edit := orchestratorpb.Edit_builder{
		Stage: &orchestratorpb.StageDelta{},
	}.Build()
	expect := populateAllValueRefs(edit, Stage)

	var found int
	for range RefsIn(edit) {
		found++
	}

	if found != expect {
		t.Errorf("got %d, want %d", found, expect)
	}
}

// TestRefsInCheck ensures that `RefsIn` actually covers all ValueRefs in the
// Check proto, traversing Check.results in reverse order.
//
// If this test fails, it likely means that protobufs for orchestrator.Check
// have changed and RefsIn needs to be updated.
func TestRefsInCheck(t *testing.T) {
	check := &orchestratorpb.Check{}
	expect := populateAllValueRefs(check, Check)

	checkID := ids.Check("C1")
	res0ID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(1)}.Build()
	res1ID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(2)}.Build()
	editResID := idspb.CheckResult_builder{Check: checkID, Idx: proto.Int32(3)}.Build()
	ts := timestamppb.New(time.Unix(100, 0))
	actor0 := orchestratorpb.Actor_builder{
		WorkplanCreator: &orchestratorpb.Actor_WorkplanCreator{},
	}.Build()
	actor1 := orchestratorpb.Actor_builder{
		Orchestrator: &orchestratorpb.Actor_Orchestrator{},
	}.Build()

	check.SetIdentifier(checkID)
	res0 := check.GetResults()[0]
	res0.SetIdentifier(res0ID)
	res0.SetOwner(actor0)
	res1 := proto.CloneOf(res0)
	res1.SetIdentifier(res1ID)
	res1.SetOwner(actor1)
	check.SetResults([]*orchestratorpb.Check_Result{res0, res1})
	expect++

	check.GetEdits()[0].SetForNode(ids.Wrap(checkID))
	check.GetEdits()[0].SetVersion(orchestratorpb.Revision_builder{Ts: ts}.Build())
	check.GetEdits()[0].GetCheck().GetResults()[0].SetIdentifier(editResID)

	var got []RefContext
	for ctx := range RefsIn(check) {
		got = append(got, ctx)
	}

	if len(got) != expect {
		t.Fatalf("got %d, want %d", len(got), expect)
	}
	editID := ids.Wrap(idspb.CheckEdit_builder{Check: checkID, Version: ts}.Build())
	want := []RefContext{
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, id: ids.Wrap(checkID)},
		&ResultDataRefContext{
			CommonRefContext: CommonRefContext{
				slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
				id:   ids.Wrap(res1ID),
			},
			Idx:   1,
			Actor: actor1,
		},
		&ResultDataRefContext{
			CommonRefContext: CommonRefContext{
				slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
				id:   ids.Wrap(res0ID),
			},
			Idx:   0,
			Actor: actor0,
		},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL, id: editID},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION, id: editID},
		&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA, id: ids.Wrap(editResID)},
	}
	if diff := cmp.Diff(want, got, cmp.AllowUnexported(CommonRefContext{}), protocmp.Transform()); diff != "" {
		t.Errorf("RefsIn(Check) mismatch (-want +got):\n%s", diff)
	}
	if got[0].Slot() != orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION {
		t.Errorf("got[0].Slot() = %v, want %v", got[0].Slot(), orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION)
	}
	if !proto.Equal(got[0].Id(), ids.Wrap(checkID)) {
		t.Errorf("got[0].Id() = %v, want %v", got[0].Id(), ids.Wrap(checkID))
	}
}

// TestRefsInCheckEdit ensures that `RefsIn` actually covers all ValueRefs in
// the Check Edit proto.
//
// If this test fails, it likely means that protobufs for orchestrator.Edit
// have changed and RefsIn needs to be updated.
func TestRefsInCheckEdit(t *testing.T) {
	edit := orchestratorpb.Edit_builder{
		Check: orchestratorpb.CheckDelta_builder{
			State: orchestratorpb.CheckState_CHECK_STATE_FINAL.Enum(),
		}.Build(),
	}.Build()
	expect := populateAllValueRefs(edit, Check)

	var found int
	for range RefsIn(edit) {
		found++
	}

	if found != expect {
		t.Errorf("got %d, want %d", found, expect)
	}
}
