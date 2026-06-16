// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Package ids has helper functions for working with TurboCI identifier messages.
//
// Of particular note is ToString/FromString and which will parse to and from
// the canonical string representation of all objects in the ids.v1 namespace.
package ids

import (
	"fmt"
	"slices"
	"strings"

	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

const Invalid = "<turboci invalid identifier>"

// ToString converts any TurboCI identifier proto into a string.
//
// The string format is defined in [identifier.proto].
//
// For stages without `is_worknode` set, this will generate string IDs like:
//
//	L123456789:?stage id
//
// These IDs are not valid for reading or writing to the graph, but are a useful
// intermediate/local representation for stages whose worknode-ness is unknown.
//
// Returns [Invalid] for nil identifiers.
//
// [identifier.proto]: https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/ids/v1/identifier.proto
func ToString[Id Identifier](id Id) string {
	if id == nil {
		return Invalid
	}

	anyID := unwrap(id)

	fmtVersion := func(ts *timestamppb.Timestamp) string {
		return fmt.Sprintf("%d/%d", ts.GetSeconds(), ts.GetNanos())
	}

	// will accumulate tokens in reverse order to be joined with ''.
	//
	// 4 tokens is the deepest this should ever get; double it to account for
	// separators.
	acc := make([]string, 0, 4*2)

	for stop := false; !stop; {
		switch x := anyID.(type) {
		case *idspb.WorkPlan:
			if x.HasId() {
				acc = append(acc, "L"+x.GetId())
			}
			stop = true

		case *idspb.Check:
			acc = append(acc, x.GetId(), ":C")
			anyID = x.GetWorkPlan()

		case *idspb.CheckResult:
			acc = append(acc, fmt.Sprint(x.GetIdx()), ":R")
			anyID = x.GetCheck()

		case *idspb.CheckEdit:
			acc = append(acc, fmtVersion(x.GetVersion()), ":V")
			anyID = x.GetCheck()

		case *idspb.Stage:
			sep := ":?"
			if x.HasIsWorknode() {
				if x.GetIsWorknode() {
					sep = ":N"
				} else {
					sep = ":S"
				}
			}
			acc = append(acc, x.GetId(), sep)
			anyID = x.GetWorkPlan()

		case *idspb.StageAttempt:
			acc = append(acc, fmt.Sprint(x.GetIdx()), ":A")
			anyID = x.GetStage()

		case *idspb.StageEdit:
			acc = append(acc, fmtVersion(x.GetVersion()), ":V")
			anyID = x.GetStage()

		default:
			panic(fmt.Sprintf("impossible type: %T", id))
		}
	}

	slices.Reverse(acc)
	return strings.Join(acc, "")
}
