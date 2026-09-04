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

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestSetAddIn(t *testing.T) {
	t.Parallel()

	s, err := structpb.NewStruct(map[string]any{"hello": "world"})
	assert.NoErr(t, err)

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
		assert.False(t, realmConflict)
	}

	assert.Match(t, []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)

	set, realmConflict := SetByTypeIn(set, MustInline(structpb.NewBoolValue(false), "other:realm"))
	assert.True(t, realmConflict)

	assert.Match(t, []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)

	set, added := AddByTypeIn(set, MustInline(structpb.NewBoolValue(true), "proj:realm"))
	assert.False(t, added)

	set, added = AddByTypeIn(set, MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"))
	assert.True(t, added)

	assert.Match(t, []*orchestratorpb.ValueRef{
		MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"),
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}, set)
}
