// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Package ids has helper functions for working with TurboCI identifier messages.
//
// Of particular note is ToString/FromString and which will parse to and from
// the canonical string representation of all objects in the ids.v1 namespace.
package ids

import (
	"errors"
	"fmt"
	"slices"
	"strings"

	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

// ErrInvalidIdentifier is the core error returned from ToStringErr if the
// identifier is invalid (i.e. `errors.Is` will find it).
var ErrInvalidIdentifier = errors.New("turboci invalid identifier")

// ToStringErr converts any TurboCI identifier proto into a string.
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
// Returns an error derived from [ErrInvalidIdentifier] for all bad identifiers.
// For logging/display purposes, consider [ToString] instead which renders all
// such errors as `"<" + err.Error() + ">"`.
//
// [identifier.proto]: https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/ids/v1/identifier.proto
func ToStringErr[Id Identifier](id Id) (string, error) {
	if id == nil {
		return "", fmt.Errorf("%w: id was nil", ErrInvalidIdentifier)
	}

	anyID := unwrap(id)
	if anyID == nil {
		return "", fmt.Errorf("%w: id could not be unwrapped", ErrInvalidIdentifier)
	}

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
			if x.GetId() != "" {
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

	if len(acc) == 0 {
		return "", fmt.Errorf("%w: id was empty", ErrInvalidIdentifier)
	}

	slices.Reverse(acc)
	return strings.Join(acc, ""), nil
}

// ToString is the error-less counterpart of [ToStringErr]. All errors are
// rendered as `"<" + err.Error() + ">"`.
func ToString[Id Identifier](id Id) string {
	ret, err := ToStringErr(id)
	if err != nil {
		return "<" + err.Error() + ">"
	}
	return ret
}
