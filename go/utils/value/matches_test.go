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
)

func TestWriteMatchesRef(t *testing.T) {
	t.Parallel()

	data1, _ := anypb.New(&emptypb.Empty{})
	data2, _ := anypb.New(&structpb.Struct{})

	t.Run(`match inline`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.True(t, WriteMatchesRef(write, ref))
	})

	t.Run(`match digest`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(string(ComputeDigest(data1))),
		}.Build()
		assert.True(t, WriteMatchesRef(write, ref))
	})

	t.Run(`mismatch realm`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm1"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm2"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.False(t, WriteMatchesRef(write, ref))
	})

	t.Run(`mismatch type url`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data2.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.False(t, WriteMatchesRef(write, ref))
	})

	t.Run(`mismatch inline data`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data2,
		}.Build()
		assert.False(t, WriteMatchesRef(write, ref))
	})

	t.Run(`mismatch digest`, func(t *testing.T) {
		t.Parallel()
		write := orchestratorpb.ValueWrite_builder{
			Realm: proto.String("realm"),
			Data:  data1,
		}.Build()
		ref := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(string(ComputeDigest(data2))),
		}.Build()
		assert.False(t, WriteMatchesRef(write, ref))
	})
}

func TestRefMatchesRef(t *testing.T) {
	t.Parallel()

	data1, _ := anypb.New(&emptypb.Empty{})
	data2, _ := anypb.New(&structpb.Struct{})
	digest1 := string(ComputeDigest(data1))
	digest2 := string(ComputeDigest(data2))

	t.Run(`match inline-inline`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.True(t, RefMatchesRef(a, b))
	})

	t.Run(`match inline-digest`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest1),
		}.Build()
		assert.True(t, RefMatchesRef(a, b))
	})

	t.Run(`match digest-inline`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest1),
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.True(t, RefMatchesRef(a, b))
	})

	t.Run(`match digest-digest`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest1),
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest1),
		}.Build()
		assert.True(t, RefMatchesRef(a, b))
	})

	t.Run(`mismatch realm`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm1"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm2"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		assert.False(t, RefMatchesRef(a, b))
	})

	t.Run(`mismatch type url`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String("type1"),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String("type2"),
			Inline:  data1,
		}.Build()
		assert.False(t, RefMatchesRef(a, b))
	})

	t.Run(`mismatch inline data`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data2,
		}.Build()
		assert.False(t, RefMatchesRef(a, b))
	})

	t.Run(`mismatch digest`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest1),
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Digest:  proto.String(digest2),
		}.Build()
		assert.False(t, RefMatchesRef(a, b))
	})

	t.Run(`one missing content`, func(t *testing.T) {
		t.Parallel()
		a := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
			Inline:  data1,
		}.Build()
		b := orchestratorpb.ValueRef_builder{
			Realm:   proto.String("realm"),
			TypeUrl: proto.String(data1.TypeUrl),
		}.Build()
		assert.False(t, RefMatchesRef(a, b))
	})
}
