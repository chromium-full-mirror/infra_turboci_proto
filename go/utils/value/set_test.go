// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/wrapperspb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestSetAddIn(t *testing.T) {
	t.Parallel()

	s, err := structpb.NewStruct(map[string]any{"hello": "world"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

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
		if realmConflict {
			t.Errorf("expected realmConflict to be false")
		}
	}

	want := []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}
	if diff := cmp.Diff(want, set, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	set, realmConflict := SetByTypeIn(set, MustInline(structpb.NewBoolValue(false), "other:realm"))
	if !realmConflict {
		t.Errorf("expected realmConflict to be true")
	}

	if diff := cmp.Diff(want, set, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	set, added := AddByTypeIn(set, MustInline(structpb.NewBoolValue(true), "proj:realm"))
	if added {
		t.Errorf("expected added to be false")
	}

	set, added = AddByTypeIn(set, MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"))
	if !added {
		t.Errorf("expected added to be true")
	}

	wantAfterAdd := []*orchestratorpb.ValueRef{
		MustInline(&wrapperspb.BoolValue{Value: true}, "proj:realm"),
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(s, "proj:realm"),
		MustInline(structpb.NewStringValue("goodbye"), "proj:realm"),
	}
	if diff := cmp.Diff(wantAfterAdd, set, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}
}
