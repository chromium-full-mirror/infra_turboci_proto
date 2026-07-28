// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// AccessCheck is a function provided to [ParsedFilter] to allow the caller to
// indicate when the caller does not have access to a particular ValueRef.
type AccessCheck func(realm string) (bool, error)

// ParsedFilter is a parsed representation of orchestratorpb.ValueFilter.
type ParsedFilter struct {
	// A reduced version of the ValueMasks in ValueFilter; indicates which slots
	// need data.
	//
	// This will need to be extended to e.g. a bitmask when there are more
	// filterable things in Value (such as tags).
	//
	// A bitmask indicating which slots need data.
	//
	// Note that 'TYPE' is always wanted (just the TypeURL of the ValueRef).
	needData SlotSet
	ti       *TypeInfo
}

// ParseFilter validates and preprocesses the given filter.
func ParseFilter(vf *orchestratorpb.ValueFilter) (*ParsedFilter, error) {
	ti, err := ParseTypeInfo(vf.GetTypeInfo())
	if err != nil {
		return nil, err
	}

	if len(vf.GetIncludeData()) > 0 {
		return &ParsedFilter{SlotSet{}.Set(vf.GetIncludeData()...), ti}, nil
	}

	// Fallback to legacy fields.
	// These two don't currently have a manual control in ValueMask.
	vfSet := SlotSet{}.Set(
		orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
		orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
	)

	setVF := func(slot orchestratorpb.ValueSlot, vm orchestratorpb.ValueMask) {
		if vm == orchestratorpb.ValueMask_VALUE_MASK_VALUE_TYPE {
			vfSet = vfSet.Set(slot)
		}
	}
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, vf.GetStageArgs())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE, vf.GetStageLegacyWorknode())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL, vf.GetStageAttemptDetails())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL, vf.GetStageAttemptProgressDetails())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL, vf.GetStageEditAttemptDetails())

	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, vf.GetCheckOptions())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA, vf.GetCheckResultData())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION, vf.GetCheckEditOptions())
	setVF(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA, vf.GetCheckEditResultData())

	return &ParsedFilter{vfSet, ti}, nil
}

// Apply checks if a ValueRef passes the filter.
//
// It expects a Slot and a ValueRef, and:
//   - [Omit]s the ref if the user does not have access (per `hasAccess`) or if
//     the ref is unwanted.
//   - Returns needsJSON = true if the user wants the data as JSON.
//
// The caller of the filter should consider the ref wanted if it was not
// omitted (i.e. ref.HasOmitReason() == false).
//
// If `hasAccess` is nil, access checks are disabled (meaning that no refs will
// be omitted with NO_ACCESS).
//
// See [RefsInStage], [RefsInStageAttempt] and [RefsInCheck] for iterators
// which easily compose with this.
func (pf *ParsedFilter) Apply(slot orchestratorpb.ValueSlot, ref *orchestratorpb.ValueRef, hasAccess AccessCheck) (needsJSON bool, err error) {
	access := true
	if hasAccess != nil {
		if access, err = hasAccess(ref.GetRealm()); err != nil {
			return
		}
	}
	if !access {
		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)
		return
	}
	if !pf.needData.HasAll(slot) {
		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)
		return
	}

	// At this point we *structurally* want, and can access, ref.
	// See how typeinfo deals with this.
	wanted, needsJSON := pf.ti.Wants(ref.GetTypeUrl())
	if !wanted && !needsJSON {
		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)
	}
	return
}
