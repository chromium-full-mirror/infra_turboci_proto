// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"strings"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/emptypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	testingtagspb "go.chromium.org/turboci/proto/go/testing/tags"
)

func TestWrite(t *testing.T) {
	t.Parallel()

	t.Run(`ok`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(&emptypb.Empty{})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := orchestratorpb.ValueWrite_builder{
			Data:  &anypb.Any{TypeUrl: URL[*emptypb.Empty]()},
			Realm: proto.String(RealmFromContainer),
		}.Build()
		if diff := cmp.Diff(want, vw, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`ok_with_tags`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(testingtagspb.MyMessage_builder{
			TaggedField: proto.String("hi"),
		}.Build())
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if len(vw.GetTags()) != 1 {
			t.Errorf("expected 1 tag, got %d: %v", len(vw.GetTags()), vw.GetTags())
		}
	})

	t.Run(`ok_realm`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(&emptypb.Empty{}, "project:realm")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := orchestratorpb.ValueWrite_builder{
			Data:  &anypb.Any{TypeUrl: URL[*emptypb.Empty]()},
			Realm: proto.String("project:realm"),
		}.Build()
		if diff := cmp.Diff(want, vw, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`err_two_realms`, func(t *testing.T) {
		t.Parallel()

		_, err := Write(&emptypb.Empty{}, "project:realm", "what")
		if err == nil || !strings.Contains(err.Error(), "realm provided more than once") {
			t.Fatalf("expected error containing %q, got %v", "realm provided more than once", err)
		}
	})

	t.Run(`err_any`, func(t *testing.T) {
		t.Parallel()

		_, err := Write(&anypb.Any{})
		if err == nil || !strings.Contains(err.Error(), "cannot handle google.protobuf.Any") {
			t.Fatalf("expected error containing %q, got %v", "cannot handle google.protobuf.Any", err)
		}
	})
}
