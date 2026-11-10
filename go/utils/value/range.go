// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"iter"
	"slices"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"go.chromium.org/turboci/proto/go/utils/ids"
)

// RefContext provides context about a ValueRef yielded by [RefsIn].
type RefContext interface {
	// Slot returns the ValueSlot of the yielded ValueRef.
	Slot() orchestratorpb.ValueSlot
	// Id returns the most proximal Identifier enclosing the yielded ValueRef.
	Id() *idspb.Identifier
}

// CommonRefContext is the [RefContext] implementation yielded by [RefsIn] for
// all ValueSlots other than VALUE_SLOT_CHECK_RESULT_DATA.
type CommonRefContext struct {
	slot orchestratorpb.ValueSlot
	id   *idspb.Identifier
}

// Slot returns the ValueSlot of the yielded ValueRef.
func (c *CommonRefContext) Slot() orchestratorpb.ValueSlot {
	return c.slot
}

// Id returns the most proximal Identifier enclosing the yielded ValueRef.
func (c *CommonRefContext) Id() *idspb.Identifier {
	return c.id
}

// ResultDataRefContext is the [RefContext] implementation yielded by [RefsIn]
// for ValueRefs in Check.results data (VALUE_SLOT_CHECK_RESULT_DATA).
type ResultDataRefContext struct {
	CommonRefContext

	// Idx is the 0-based index of the Check.Result in Check.results in
	// which the ValueRef was found.
	Idx int
	// Actor is the owner of the Check.Result.
	Actor *orchestratorpb.Actor
}

// RefsIn returns an iterator which iterates through all ValueRefs in the
// object.
//
// For *Check objects (including Checks within a *WorkPlan), Check.results data
// (VALUE_SLOT_CHECK_RESULT_DATA) is yielded in reverse Check.results order with
// a [*ResultDataRefContext] so the latest version of results is available
// first. In particular, if each Actor submitted more than one result, their
// most recent result will be available first. All other ValueSlots are yielded
// with a [*CommonRefContext].
//
// Object may be:
//   - *Stage
//   - *Stage_Attempt
//   - *Check
//   - *WorkPlan
//   - *Edit
//
// Otherwise this will panic.
func RefsIn(object any) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	switch x := any(object).(type) {
	case *orchestratorpb.Stage:
		return refsInStage(x)
	case *orchestratorpb.Stage_Attempt:
		return refsInStageAttempt(x)
	case *orchestratorpb.Check:
		return refsInCheck(x)
	case *orchestratorpb.WorkPlan:
		return refsInWorkplan(x)
	case *orchestratorpb.Edit:
		return refsInEdit(x)
	}
	panic(fmt.Sprintf("impossible: bad type %T", object))
}

// refsInStage is an iterator which iterates through every non-nil *ValueRef
// in the Stage.
func refsInStage(stage *orchestratorpb.Stage) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
		id := ids.Wrap(stage.GetIdentifier())
		if args := stage.GetArgs(); args != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, id: id}, args) {
			return
		}

		if worknode := stage.GetLegacy().GetWorknode(); worknode != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, id: id}, worknode) {
			return
		}

		for _, edit := range stage.GetEdits() {
			for ctx, ref := range refsInEdit(edit) {
				if ref != nil && !yield(ctx, ref) {
					return
				}
			}
		}

		for _, attempt := range stage.GetAttempts() {
			for ctx, ref := range refsInStageAttempt(attempt) {
				if ref != nil && !yield(ctx, ref) {
					return
				}
			}
		}
	}
}

// refsInStageAttempt is an iterator which iterates through every non-nil
// *ValueRef in the Stage Attempt.
func refsInStageAttempt(attempt *orchestratorpb.Stage_Attempt) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
		id := ids.Wrap(attempt.GetIdentifier())
		for _, detail := range attempt.GetDetails() {
			if detail != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL, id: id}, detail) {
				return
			}
		}
		for _, progress := range attempt.GetProgress() {
			for _, detail := range progress.GetDetails() {
				if detail != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL, id: id}, detail) {
					return
				}
			}
		}
	}
}

// refsInEdit is an iterator which iterates through every non-nil
// *ValueRef in the Edit.
func refsInEdit(edit *orchestratorpb.Edit) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	switch edit.WhichDelta() {
	case orchestratorpb.Edit_Stage_case:
		return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
			editID := ids.Wrap(idspb.StageEdit_builder{
				Stage:   edit.GetForNode().GetStage(),
				Version: edit.GetVersion().GetTs(),
			}.Build())
			for _, detail := range edit.GetReason().GetDetails() {
				if detail != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL, id: editID}, detail) {
					return
				}
			}
			for _, attempt := range edit.GetStage().GetAttempts() {
				attemptID := ids.Wrap(attempt.GetIdentifier())
				for _, detail := range attempt.GetDetails() {
					if detail != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL, id: attemptID}, detail) {
						return
					}
				}
			}
		}

	case orchestratorpb.Edit_Check_case:
		return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
			editID := ids.Wrap(idspb.CheckEdit_builder{
				Check:   edit.GetForNode().GetCheck(),
				Version: edit.GetVersion().GetTs(),
			}.Build())
			for _, detail := range edit.GetReason().GetDetails() {
				if detail != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL, id: editID}, detail) {
					return
				}
			}
			for _, option := range edit.GetCheck().GetOptions() {
				if option != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION, id: editID}, option) {
					return
				}
			}
			for _, result := range edit.GetCheck().GetResults() {
				resultID := ids.Wrap(result.GetIdentifier())
				for _, dat := range result.GetData() {
					if dat != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA, id: resultID}, dat) {
						return
					}
				}
			}
		}
	}

	panic("impossible")
}

// refsInCheck is an iterator which iterates through every non-nil
// *ValueRef in the Check.
//
// Check.results are traversed in reverse order so the latest version of results
// is available first. In particular, if each Actor submitted more than one
// result, their most recent result will be available first.
func refsInCheck(check *orchestratorpb.Check) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
		checkID := ids.Wrap(check.GetIdentifier())
		for _, option := range check.GetOptions() {
			if option != nil && !yield(&CommonRefContext{slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, id: checkID}, option) {
				return
			}
		}
		for i, r := range slices.Backward(check.GetResults()) {
			ctx := &ResultDataRefContext{
				CommonRefContext: CommonRefContext{
					slot: orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
					id:   ids.Wrap(r.GetIdentifier()),
				},
				Idx:   i,
				Actor: r.GetOwner(),
			}
			for _, dat := range r.GetData() {
				if dat != nil && !yield(ctx, dat) {
					return
				}
			}
		}
		for _, edit := range check.GetEdits() {
			for ctx, ref := range refsInEdit(edit) {
				if ref != nil && !yield(ctx, ref) {
					return
				}
			}
		}
	}
}

// refsInWorkplan is an iterator which iterates through every non-nil
// *ValueRef in the WorkPlan.
func refsInWorkplan(wp *orchestratorpb.WorkPlan) iter.Seq2[RefContext, *orchestratorpb.ValueRef] {
	return func(yield func(RefContext, *orchestratorpb.ValueRef) bool) {
		for _, stg := range wp.GetStages() {
			for ctx, ref := range refsInStage(stg) {
				if !yield(ctx, ref) {
					return
				}
			}
		}
		for _, chk := range wp.GetChecks() {
			for ctx, ref := range refsInCheck(chk) {
				if !yield(ctx, ref) {
					return
				}
			}
		}
	}
}
