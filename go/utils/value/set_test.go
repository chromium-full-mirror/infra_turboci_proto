// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/wrapperspb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestSetAddIn(t *testing.T) {
	t.Parallel()

	s, err := structpb.NewStruct(map[string]any{"hello": "world"})
	assertNoErr(t, err)

	toSet := []*orchestratorpb.ValueRef{
		// NOTE: BoolValue and StringValue are the same proto message type.
		MustInline(structpb.NewBoolValue(true), "proj:realm"),
		MustInline(structpb.NewBoolValue(false), "proj:realm"),
		MustInline(structpb.NewStringValue("hello"), "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}

	var set []*orchestratorpb.ValueRef

	for _, ref := range toSet {
		var realmConflict bool
		set, realmConflict = SetByTypeIn(set, ref)
		assertFalse(t, realmConflict)
	}

	assertMatch(t, []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)

	set, realmConflict := SetByTypeIn(set, MustInline(structpb.NewBoolValue(false), "other:realm"))
	assertTrue(t, realmConflict)

	assertMatch(t, []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)

	set, added := AddByTypeIn(set, MustInline(structpb.NewBoolValue(true), "proj:realm"))
	assertFalse(t, added)

	set, added = AddByTypeIn(set, MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"))
	assertTrue(t, added)

	assertMatch(t, []*orchestratorpb.ValueRef{
		MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"),
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)
}
