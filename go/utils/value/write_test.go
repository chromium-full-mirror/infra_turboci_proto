// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/emptypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	testingtagspb "go.chromium.org/turboci/proto/go/testing/tags"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestWrite(t *testing.T) {
	t.Parallel()

	t.Run(`ok`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(&emptypb.Empty{})
		assert.NoErr(t, err)
		assert.Match(t, orchestratorpb.ValueWrite_builder{
			Data:  &anypb.Any{TypeUrl: URL[*emptypb.Empty]()},
			Realm: proto.String(RealmFromContainer),
		}.Build(), vw)
	})

	t.Run(`ok_with_tags`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(testingtagspb.MyMessage_builder{
			TaggedField: proto.String("hi"),
		}.Build())
		assert.NoErr(t, err)
		assert.Len(t, vw.GetTags(), 1)
	})

	t.Run(`ok_realm`, func(t *testing.T) {
		t.Parallel()

		vw, err := Write(&emptypb.Empty{}, "project:realm")
		assert.NoErr(t, err)
		assert.Match(t, orchestratorpb.ValueWrite_builder{
			Data:  &anypb.Any{TypeUrl: URL[*emptypb.Empty]()},
			Realm: proto.String("project:realm"),
		}.Build(), vw)
	})

	t.Run(`err_two_realms`, func(t *testing.T) {
		t.Parallel()

		_, err := Write(&emptypb.Empty{}, "project:realm", "what")
		assert.ErrLike(t, err, "realm provided more than once")
	})

	t.Run(`err_any`, func(t *testing.T) {
		t.Parallel()

		_, err := Write(&anypb.Any{})
		assert.ErrLike(t, err, "cannot handle google.protobuf.Any")
	})
}
