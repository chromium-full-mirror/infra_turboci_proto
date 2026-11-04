// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"iter"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// RefsIn returns an iterator which iterates through all ValueRefs in the
// object.
//
// Object may be:
//   - *Stage
//   - *Stage_Attempt
//   - *Check
//   - *WorkPlan
//   - *Edit
//
// Otherwise this will panic.
func RefsIn(object any) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
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
// in the stage.
func refsInStage(stage *orchestratorpb.Stage) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		if args := stage.GetArgs(); args != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, args) {
			return
		}

		if worknode := stage.GetLegacy().GetWorknode(); worknode != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, worknode) {
			return
		}

		for _, edit := range stage.GetEdits() {
			for slot, ref := range refsInEdit(edit) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}

		for _, attempt := range stage.GetAttempts() {
			for slot, ref := range refsInStageAttempt(attempt) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}
	}
}

// refsInStageAttempt is an iterator which iterates through every non-nil
// *ValueRef in the stage attempt.
func refsInStageAttempt(attempt *orchestratorpb.Stage_Attempt) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		for _, detail := range attempt.GetDetails() {
			if detail != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL, detail) {
				return
			}
		}
		for _, progress := range attempt.GetProgress() {
			for _, detail := range progress.GetDetails() {
				if detail != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL, detail) {
					return
				}
			}
		}
	}
}

// refsInEdit is an iterator which iterates through every non-nil
// *ValueRef in the edit.
func refsInEdit(edit *orchestratorpb.Edit) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	switch edit.WhichDelta() {
	case orchestratorpb.Edit_Stage_case:
		return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
			for _, detail := range edit.GetReason().GetDetails() {
				if detail != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL, detail) {
					return
				}
			}
			for _, attempt := range edit.GetStage().GetAttempts() {
				for _, detail := range attempt.GetDetails() {
					if detail != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL, detail) {
						return
					}
				}
			}
		}

	case orchestratorpb.Edit_Check_case:
		return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
			for _, detail := range edit.GetReason().GetDetails() {
				if detail != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL, detail) {
					return
				}
			}
			for _, option := range edit.GetCheck().GetOptions() {
				if option != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION, option) {
					return
				}
			}
			for _, result := range edit.GetCheck().GetResults() {
				for _, dat := range result.GetData() {
					if dat != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA, dat) {
						return
					}
				}
			}
		}
	}

	panic("impossible")
}

// refsInCheck is an iterator which iterates through every non-nil
// *ValueRef in the check.
func refsInCheck(check *orchestratorpb.Check) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		for _, option := range check.GetOptions() {
			if option != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, option) {
				return
			}
		}
		for _, result := range check.GetResults() {
			for _, dat := range result.GetData() {
				if dat != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA, dat) {
					return
				}
			}
		}
		for _, edit := range check.GetEdits() {
			for slot, ref := range refsInEdit(edit) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}
	}
}

// refsInWorkplan is an iterator which iterates through every non-nil
// *ValueRef in the WorkPlan.
func refsInWorkplan(wp *orchestratorpb.WorkPlan) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		for _, stg := range wp.GetStages() {
			for slot, ref := range refsInStage(stg) {
				if !yield(slot, ref) {
					return
				}
			}
		}
		for _, chk := range wp.GetChecks() {
			for slot, ref := range refsInCheck(chk) {
				if !yield(slot, ref) {
					return
				}
			}
		}
	}
}
