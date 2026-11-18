// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"cmp"
	"fmt"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

// Compare compares identifiers.
//
// This is equivalent to `strings.Compare(ids.ToString(a), ids.ToString(b))` but
// faster to evaluate for some common cases (like comparing Stages and Checks
// to each other).
//
// Panics if given a broken identifier.
func Compare(a, b *idspb.Identifier) int {
	extractParts := func(id *idspb.Identifier) (bool, string, string, string) {
		if check := id.GetCheck(); check != nil {
			return true, check.GetWorkPlan().GetId(), "C", check.GetId()
		}
		if stage := id.GetStage(); stage != nil {
			wn := "?"
			if stage.GetIsWorknode() {
				wn = "N"
			} else if stage.HasIsWorknode() {
				wn = "S"
			}
			return true, stage.GetWorkPlan().GetId(), wn, stage.GetId()
		}
		return false, "", "", ""
	}
	okA, planA, kindA, nodeA := extractParts(a)
	okB, planB, kindB, nodeB := extractParts(b)

	// Fast path for Stages and Checks, the most common use of this function.
	if okA && okB {
		return cmp.Or(
			cmp.Compare(planA, planB),
			cmp.Compare(kindA, kindB),
			cmp.Compare(nodeA, nodeB),
		)
	}

	// Generic slow comparison that does allocations for everything else.
	aStr, aErr := ToStringErr(a)
	if aErr != nil {
		panic(fmt.Sprintf("bad Identifier: %s", aErr))
	}
	bStr, bErr := ToStringErr(b)
	if bErr != nil {
		panic(fmt.Sprintf("bad Identifier: %s", bErr))
	}
	return cmp.Compare(aStr, bStr)
}
