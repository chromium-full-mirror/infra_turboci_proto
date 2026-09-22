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
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestInline(t *testing.T) {
	t.Parallel()

	t.Run(`nil`, func(t *testing.T) {
		t.Parallel()

		_, err := Inline(nil, "proj:realm")
		if err == nil || !strings.Contains(err.Error(), "nil source message") {
			t.Fatalf("expected error containing %q, got %v", "nil source message", err)
		}
	})

	t.Run(`ok`, func(t *testing.T) {
		t.Parallel()

		sval := structpb.NewStringValue("hello")
		svalAny, err := anypb.New(sval)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		svalBytes, err := proto.Marshal(sval)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		want := orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Realm:   proto.String("proj:realm"),
			Inline: &anypb.Any{
				TypeUrl: URL[*structpb.Value](),
				Value:   svalBytes,
			},
			Digest: proto.String(string(ComputeDigest(svalAny))),
		}.Build()
		if diff := cmp.Diff(want, MustInline(sval, "proj:realm"), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`any`, func(t *testing.T) {
		t.Parallel()

		sval := structpb.NewStringValue("hello")
		svalAny, err := anypb.New(sval)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		want := orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Realm:   proto.String("proj:realm"),
			Inline:  svalAny,
			Digest:  proto.String(string(ComputeDigest(svalAny))),
		}.Build()
		if diff := cmp.Diff(want, MustInline(sval, "proj:realm"), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})
}

func TestAbsorbInline(t *testing.T) {
	t.Parallel()

	dSrc := SimpleDataSource{}

	ref := MustInline(structpb.NewStringValue("hello"), "proj:realm")

	if !ref.HasInline() {
		t.Errorf("expected ref.HasInline() to be true")
	}

	origBinData := ref.GetInline()

	AbsorbInline(dSrc, ref)

	// ref now contains the digest
	wantDigest := Digest("Umz0vGbOEPay3Z8mD9wDfGKojbSTVMQMyosq3zgqszk0AQ")
	if got := ref.GetDigest(); got != string(wantDigest) {
		t.Errorf("got digest %q, want %q", got, wantDigest)
	}

	// dSrc now has the data and it's identical.
	//
	// Note that DataSource avoids copying the data and will return the
	// identical pointer which was in `ref`.
	if got := dSrc.Retrieve(wantDigest).GetBinary(); got != origBinData {
		t.Errorf("got binary %v, want %v", got, origBinData)
	}

	// Absorbing again is a no-op.
	AbsorbInline(dSrc, ref)
}
