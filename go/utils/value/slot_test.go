// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"slices"
	"testing"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestValueSlotSet(t *testing.T) {

	t.Parallel()

	t.Run("zero_value", func(t *testing.T) {
		t.Parallel()
		var s SlotSet
		assert.Equal(t, uint64(0), s.val)
		assert.Empty(t, slices.Collect(s.Range()))
		assert.Equal(t, "value.SlotSet{}", s.String())
		assert.False(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
		assert.False(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
	})

	t.Run("set_unset_immutability", func(t *testing.T) {
		t.Parallel()
		var s1 SlotSet
		s2 := s1.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)
		assert.Equal(t, uint64(0), s1.val)
		assert.Equal(t, uint64((1<<0)|(1<<5)), s2.val)

		s3 := s2.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION)
		assert.Equal(t, uint64((1<<0)|(1<<5)), s2.val)
		assert.Equal(t, uint64(1<<5), s3.val)
	})

	t.Run("containment", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)

		assert.True(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
		assert.True(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS))
		assert.False(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA))

		assert.True(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
		assert.True(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA))
		assert.False(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA))
	})

	t.Run("unknown_and_duplicates", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(
			orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
		)
		assert.Equal(t, uint64(1<<0), s.val)
		assert.True(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
		assert.True(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
	})

	t.Run("out_of_bounds_panics", func(t *testing.T) {
		t.Parallel()
		assert.PanicLike(t, func() {
			SlotSet{}.Set(orchestratorpb.ValueSlot(-1))
		}, "slot out of range")

		assert.PanicLike(t, func() {
			SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		}, "slot out of range")

		assert.PanicLike(t, func() {
			SlotSet{}.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		}, "slot out of range")

		assert.PanicLike(t, func() {
			SlotSet{}.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		}, "slot out of range")

		assert.PanicLike(t, func() {
			SlotSet{}.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		}, "slot out of range")
	})

	t.Run("slot_all", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_ALL)
		assert.Equal(t, slotsAll, s.val)
		assert.True(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL))
		assert.True(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL))

		assert.True(t, s.HasAll(
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_RESULT_DATA,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_LEGACY_WORKNODE,
			orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
		))

		s = s.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_ALL)
		assert.Equal(t, uint64(0), s.val)
		assert.False(t, s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL))
		assert.False(t, s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL))
	})

	t.Run("cross_language_invariance_vector", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
			orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
			orchestratorpb.ValueSlot(64),
		)
		assert.Equal(t, uint64(0x8000000000000583), s.val)
	})

	t.Run("formatting", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)
		assert.Equal(t, "value.SlotSet{CHECK_OPTION, STAGE_ARGS}", s.String())
	})

	t.Run("round_trip", func(t *testing.T) {
		t.Parallel()
		s1 := SlotSet{}.Set(
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA,
			orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS,
		)
		slots := slices.Collect(s1.Range())
		s2 := SlotSet{}.Set(slots...)
		assert.Equal(t, s1.val, s2.val)
	})
}
