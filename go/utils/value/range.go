// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"iter"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// RefsInStage is an iterator which iterates through every non-nil *ValueRef
// in the stage.
func RefsInStage(stage *orchestratorpb.Stage) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		if args := stage.GetArgs(); args != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, args) {
			return
		}

		if worknode := stage.GetLegacy().GetWorknode(); worknode != nil && !yield(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, worknode) {
			return
		}

		for _, edit := range stage.GetEdits() {
			for slot, ref := range RefsInEdit(edit) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}

		for _, attempt := range stage.GetAttempts() {
			for slot, ref := range RefsInStageAttempt(attempt) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}
	}
}

// RefsInStageAttempt is an iterator which iterates through every non-nil
// *ValueRef in the stage attempt.
func RefsInStageAttempt(attempt *orchestratorpb.Stage_Attempt) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
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

// RefsInEdit is an iterator which iterates through every non-nil
// *ValueRef in the edit.
func RefsInEdit(edit *orchestratorpb.Edit) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
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

// RefsInCheck is an iterator which iterates through every non-nil
// *ValueRef in the check.
func RefsInCheck(check *orchestratorpb.Check) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
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
			for slot, ref := range RefsInEdit(edit) {
				if ref != nil && !yield(slot, ref) {
					return
				}
			}
		}
	}
}

// RefsInWorkplan is an iterator which iterates through every non-nil
// *ValueRef in the WorkPlan.
func RefsInWorkplan(wp *orchestratorpb.WorkPlan) iter.Seq2[orchestratorpb.ValueSlot, *orchestratorpb.ValueRef] {
	return func(yield func(orchestratorpb.ValueSlot, *orchestratorpb.ValueRef) bool) {
		for _, stg := range wp.GetStages() {
			for slot, ref := range RefsInStage(stg) {
				if !yield(slot, ref) {
					return
				}
			}
		}
		for _, chk := range wp.GetChecks() {
			for slot, ref := range RefsInCheck(chk) {
				if !yield(slot, ref) {
					return
				}
			}
		}
	}
}
