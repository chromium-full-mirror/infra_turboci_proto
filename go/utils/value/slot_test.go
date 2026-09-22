// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"slices"
	"strings"
	"testing"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestValueSlotSet(t *testing.T) {
	t.Parallel()

	t.Run("zero_value", func(t *testing.T) {
		t.Parallel()
		var s SlotSet
		if s.val != 0 {
			t.Errorf("got %d, want 0", s.val)
		}
		if got := slices.Collect(s.Range()); len(got) != 0 {
			t.Errorf("expected empty slice, got %v", got)
		}
		if got, want := s.String(), "value.SlotSet{}"; got != want {
			t.Errorf("got %q, want %q", got, want)
		}
		if s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAll to be false")
		}
		if s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAny to be false")
		}
	})

	t.Run("set_unset_immutability", func(t *testing.T) {
		t.Parallel()
		var s1 SlotSet
		s2 := s1.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)
		if s1.val != 0 {
			t.Errorf("got %d, want 0", s1.val)
		}
		if want := uint64((1 << 0) | (1 << 5)); s2.val != want {
			t.Errorf("got %d, want %d", s2.val, want)
		}

		s3 := s2.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION)
		if want := uint64((1 << 0) | (1 << 5)); s2.val != want {
			t.Errorf("got %d, want %d", s2.val, want)
		}
		if want := uint64(1 << 5); s3.val != want {
			t.Errorf("got %d, want %d", s3.val, want)
		}
	})

	t.Run("containment", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)

		if !s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAll(CHECK_OPTION) to be true")
		}
		if !s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS) {
			t.Errorf("expected HasAll(CHECK_OPTION, STAGE_ARGS) to be true")
		}
		if s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA) {
			t.Errorf("expected HasAll(CHECK_OPTION, CHECK_RESULT_DATA) to be false")
		}

		if !s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAny(CHECK_OPTION) to be true")
		}
		if !s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA) {
			t.Errorf("expected HasAny(CHECK_OPTION, CHECK_RESULT_DATA) to be true")
		}
		if s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_RESULT_DATA) {
			t.Errorf("expected HasAny(CHECK_RESULT_DATA) to be false")
		}
	})

	t.Run("unknown_and_duplicates", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(
			orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
			orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION,
		)
		if want := uint64(1 << 0); s.val != want {
			t.Errorf("got %d, want %d", s.val, want)
		}
		if !s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAll(UNKNOWN, CHECK_OPTION) to be true")
		}
		if !s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN, orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected HasAny(UNKNOWN, CHECK_OPTION) to be true")
		}
	})

	t.Run("out_of_bounds_panics", func(t *testing.T) {
		t.Parallel()
		checkPanic := func(f func()) {
			t.Helper()
			defer func() {
				r := recover()
				if r == nil || !strings.Contains(fmt.Sprint(r), "slot out of range") {
					t.Errorf("expected panic containing %q, got: %v", "slot out of range", r)
				}
			}()
			f()
		}

		checkPanic(func() {
			SlotSet{}.Set(orchestratorpb.ValueSlot(-1))
		})
		checkPanic(func() {
			SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		})
		checkPanic(func() {
			SlotSet{}.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		})
		checkPanic(func() {
			SlotSet{}.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		})
		checkPanic(func() {
			SlotSet{}.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL + 1)
		})
	})

	t.Run("slot_all", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_ALL)
		if s.val != slotsAll {
			t.Errorf("got %d, want %d", s.val, slotsAll)
		}
		if !s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL) {
			t.Errorf("expected HasAll(ALL) to be true")
		}
		if !s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL) {
			t.Errorf("expected HasAny(ALL) to be true")
		}

		if !s.HasAll(
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
		) {
			t.Errorf("expected HasAll(all known slots) to be true")
		}

		s = s.Unset(orchestratorpb.ValueSlot_VALUE_SLOT_ALL)
		if s.val != 0 {
			t.Errorf("got %d, want 0", s.val)
		}
		if s.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_ALL) {
			t.Errorf("expected HasAll(ALL) to be false")
		}
		if s.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_ALL) {
			t.Errorf("expected HasAny(ALL) to be false")
		}
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
		if want := uint64(0x8000000000000583); s.val != want {
			t.Errorf("got %x, want %x", s.val, want)
		}
	})

	t.Run("formatting", func(t *testing.T) {
		t.Parallel()
		s := SlotSet{}.Set(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION, orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS)
		if got, want := s.String(), "value.SlotSet{CHECK_OPTION, STAGE_ARGS}"; got != want {
			t.Errorf("got %q, want %q", got, want)
		}
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
		if s1.val != s2.val {
			t.Errorf("got %d, want %d", s2.val, s1.val)
		}
	})
}
