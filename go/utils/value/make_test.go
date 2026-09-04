// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestInline(t *testing.T) {
	t.Parallel()

	t.Run(`nil`, func(t *testing.T) {
		t.Parallel()

		_, err := Inline(nil, "proj:realm")
		assert.ErrLike(t, err, "nil source message")
	})

	t.Run(`ok`, func(t *testing.T) {
		t.Parallel()

		sval := structpb.NewStringValue("hello")
		svalAny, err := anypb.New(sval)
		assert.NoErr(t, err)
		svalBytes, err := proto.Marshal(sval)
		assert.NoErr(t, err)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Realm:   proto.String("proj:realm"),
			Inline: &anypb.Any{
				TypeUrl: URL[*structpb.Value](),
				Value:   svalBytes,
			},
			Digest: proto.String(string(ComputeDigest(svalAny))),
		}.Build(), MustInline(sval, "proj:realm"))
	})

	t.Run(`any`, func(t *testing.T) {
		t.Parallel()

		sval := structpb.NewStringValue("hello")
		svalAny, err := anypb.New(sval)
		assert.NoErr(t, err)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Realm:   proto.String("proj:realm"),
			Inline:  svalAny,
			Digest:  proto.String(string(ComputeDigest(svalAny))),
		}.Build(), MustInline(sval, "proj:realm"))
	})
}

func TestAbsorbInline(t *testing.T) {
	t.Parallel()

	dSrc := SimpleDataSource{}

	ref := MustInline(structpb.NewStringValue("hello"), "proj:realm")

	assert.True(t, ref.HasInline())

	origBinData := ref.GetInline()

	AbsorbInline(dSrc, ref)

	// ref now contains the digest
	wantDigest := Digest("Umz0vGbOEPay3Z8mD9wDfGKojbSTVMQMyosq3zgqszk0AQ")
	assert.Equal(t, string(wantDigest), ref.GetDigest())

	// dSrc now has the data and it's identical.
	//
	// Note that DataSource avoids copying the data and will return the
	// identical pointer which was in `ref`.
	assert.Equal(t, origBinData, dSrc.Retrieve(wantDigest).GetBinary())

	// Absorbing again is a no-op.
	AbsorbInline(dSrc, ref)
}
