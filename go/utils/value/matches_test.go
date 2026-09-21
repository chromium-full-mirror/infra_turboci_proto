// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
	"go.chromium.org/turboci/proto/go/utils/tags"
)

func TestWriteMatchesRef(t *testing.T) {
	t.Parallel()

	data1, _ := anypb.New(&emptypb.Empty{})
	data2, _ := anypb.New(&structpb.Struct{})
	digest1 := string(ComputeDigest(data1))
	digest2 := string(ComputeDigest(data2))

	tags1 := tags.MakeMap(
		tags.Builder{Key: "t1", Strings: []string{"t1hi"}}.Build(),
		tags.Builder{Key: "t2", Strings: []string{"t2hi"}}.Build(),
	).Proto()
	tags2 := tags.MakeMap(
		tags.Builder{Key: "t1", Strings: []string{"other"}}.Build(),
	).Proto()

	cases := []struct {
		name               string
		write              *orchestratorpb.ValueWrite
		ref                *orchestratorpb.ValueRef
		matchesWithoutTags bool
		matchesWithTags    bool
	}{
		{
			name: "no-match inline-only",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
				Tags:  tags1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
				Tags:    tags1,
			}.Build(),
			// False because digest is always required.
		},
		{
			name: "match digest",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
				Tags:  tags1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags1,
			}.Build(),
			matchesWithoutTags: true,
			matchesWithTags:    true,
		},
		{
			name: "match inline+digest",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
				Tags:  tags1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
				Digest:  proto.String(digest1),
				Tags:    tags1,
			}.Build(),
			matchesWithoutTags: true,
			matchesWithTags:    true,
		},
		{
			name: "mismatch tags",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
				Tags:  tags1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags2,
			}.Build(),
			matchesWithoutTags: true,
		},
		{
			name: "mismatch realm",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm1"),
				Data:  data1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm2"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
		},
		{
			name: "mismatch type url",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data2.TypeUrl),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
		},
		{
			name: "mismatch inline data",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Inline:  data2,
			}.Build(),
		},
		{
			name: "mismatch digest",
			write: orchestratorpb.ValueWrite_builder{
				Realm: proto.String("realm"),
				Data:  data1,
			}.Build(),
			ref: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest2),
			}.Build(),
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			assert.Equal(t, tc.matchesWithoutTags, WriteMatchesRef(tc.write, tc.ref, WithoutTagMatch))
			assert.Equal(t, tc.matchesWithTags, WriteMatchesRef(tc.write, tc.ref, WithTagMatch))
		})
	}
}

func TestRefMatchesRef(t *testing.T) {
	t.Parallel()

	data1, _ := anypb.New(&emptypb.Empty{})
	data2, _ := anypb.New(&structpb.Struct{})
	digest1 := string(ComputeDigest(data1))
	digest2 := string(ComputeDigest(data2))

	tags1 := tags.MakeMap(
		tags.Builder{Key: "t1", Strings: []string{"t1hi"}}.Build(),
		tags.Builder{Key: "t2", Strings: []string{"t2hi"}}.Build(),
	).Proto()
	tags2 := tags.MakeMap(
		tags.Builder{Key: "t1", Strings: []string{"other"}}.Build(),
	).Proto()

	cases := []struct {
		name               string
		a                  *orchestratorpb.ValueRef
		b                  *orchestratorpb.ValueRef
		matchesWithoutTags bool
		matchesWithTags    bool
	}{
		{
			name: "match inline-inline",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			// False because digest is always required.
		},
		{
			name: "match inline-digest",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
			}.Build(),
			// False because digest is always required.
		},
		{
			name: "match digest-inline",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			// False because digest is always required.
		},
		{
			name: "match digest-digest",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags1,
			}.Build(),
			matchesWithoutTags: true,
			matchesWithTags:    true,
		},
		{
			name: "mismatch tags",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Tags:    tags2,
			}.Build(),
			matchesWithoutTags: true,
		},
		{
			name: "mismatch realm",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm1"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm2"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
		},
		{
			name: "mismatch type url",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String("type1"),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String("type2"),
				Digest:  proto.String(digest1),
				Inline:  data1,
			}.Build(),
		},
		{
			name: "mismatch inline data",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data2,
			}.Build(),
		},
		{
			name: "mismatch digest",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest1),
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Digest:  proto.String(digest2),
			}.Build(),
		},
		{
			name: "one missing content",
			a: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
				Inline:  data1,
			}.Build(),
			b: orchestratorpb.ValueRef_builder{
				Realm:   proto.String("realm"),
				TypeUrl: proto.String(data1.TypeUrl),
			}.Build(),
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			assert.Equal(t, tc.matchesWithoutTags, RefMatchesRef(tc.a, tc.b, WithoutTagMatch))
			assert.Equal(t, tc.matchesWithTags, RefMatchesRef(tc.a, tc.b, WithTagMatch))
		})
	}
}
