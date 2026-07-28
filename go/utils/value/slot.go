// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"iter"
	"math/bits"
	"strings"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// SlotSet represents a set of ValueSlot enums as a bitmask.
//
// Zero-value SlotSet represents an empty set. Slot N (> 0) sets bit N-1.
// UNKNOWN (0) is ignored.
//
// Panics on invalid ValueSlot values.
type SlotSet struct {
	val uint64
}

// slotsAll is all non-UNKNOWN, non-ALL value ref slot values unioned into a
// single SlotSet.
var slotsAll uint64

func init() {
	vrSlots := make([]orchestratorpb.ValueSlot, 0, len(orchestratorpb.ValueSlot_name))
	for val := range orchestratorpb.ValueSlot_name {
		slot := orchestratorpb.ValueSlot(val)
		if slot == orchestratorpb.ValueSlot_VALUE_SLOT_UNKNOWN || slot == orchestratorpb.ValueSlot_VALUE_SLOT_ALL {
			continue
		}
		vrSlots = append(vrSlots, slot)
	}
	slotsAll = SlotSet{}.Set(vrSlots...).val
}

func assertSlotIsValid(slot orchestratorpb.ValueSlot) bool {
	if slot < 0 || slot > 65 {
		panic(fmt.Sprintf("slot out of range [0, 65]: %d", slot))
	}
	return slot != 0
}

// HasAll returns true if all specified slots are present in the SlotSet.
func (s SlotSet) HasAll(slots ...orchestratorpb.ValueSlot) bool {
	for _, slot := range slots {
		if assertSlotIsValid(slot) {
			if slot == 65 {
				return (s.val & slotsAll) == slotsAll
			}
			if s.val&(1<<(uint64(slot)-1)) == 0 {
				return false
			}
		}
	}
	return true
}

// HasAny returns true if at least one of the specified slots is present in the SlotSet.
func (s SlotSet) HasAny(slots ...orchestratorpb.ValueSlot) bool {
	for _, slot := range slots {
		if assertSlotIsValid(slot) {
			if slot == 65 {
				return (s.val & slotsAll) != 0
			}
			if s.val&(1<<(uint64(slot)-1)) != 0 {
				return true
			}
		}
	}
	return false
}

// Set returns a new SlotSet with the specified slots added.
func (s SlotSet) Set(slots ...orchestratorpb.ValueSlot) SlotSet {
	mask := s.val
	for _, slot := range slots {
		if slot == 65 {
			return SlotSet{slotsAll}
		}
		if assertSlotIsValid(slot) {
			mask |= 1 << (uint64(slot) - 1)
		}
	}
	return SlotSet{mask}
}

// Unset returns a new SlotSet with the specified slots removed.
func (s SlotSet) Unset(slots ...orchestratorpb.ValueSlot) SlotSet {
	mask := s.val
	for _, slot := range slots {
		if slot == 65 {
			return SlotSet{}
		}
		if assertSlotIsValid(slot) {
			mask &^= 1 << (uint64(slot) - 1)
		}
	}
	return SlotSet{mask}
}

// Range returns an iterator yielding slot enums present in the SlotSet in
// ascending order.
func (s SlotSet) Range() iter.Seq[orchestratorpb.ValueSlot] {
	return func(yield func(orchestratorpb.ValueSlot) bool) {
		mask := s.val
		for mask != 0 {
			tz := bits.TrailingZeros64(mask)
			if !yield(orchestratorpb.ValueSlot(tz + 1)) {
				return
			}
			mask &= mask - 1
		}
	}
}

func (s SlotSet) String() string {
	var names []string
	for slot := range s.Range() {
		names = append(names, strings.TrimPrefix(slot.String(), "VALUE_SLOT_"))
	}
	return fmt.Sprintf("value.SlotSet{%s}", strings.Join(names, ", "))
}
