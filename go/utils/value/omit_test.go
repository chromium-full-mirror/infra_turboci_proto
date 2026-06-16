// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/internal/test/assert"
)

func TestOmit(t *testing.T) {
	t.Parallel()

	t.Run(`inline_unwanted`, func(t *testing.T) {
		t.Parallel()

		ref := MustInline(structpb.NewStringValue("hi"), "proj:realm")
		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl:    proto.String(URL[*structpb.Value]()),
			Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
			OmitReason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED.Enum(),
			Realm:      proto.String("proj:realm"),
		}.Build(), ref)
	})

	t.Run(`inline_noaccess`, func(t *testing.T) {
		t.Parallel()

		ref := MustInline(structpb.NewStringValue("hi"), "proj:realm")
		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl:    proto.String(URL[*structpb.Value]()),
			OmitReason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS.Enum(),
			Realm:      proto.String("proj:realm"),
		}.Build(), ref)
	})

	t.Run(`outboard_unwanted`, func(t *testing.T) {
		t.Parallel()
		dSrc := SimpleDataSource{}

		ref := MustInline(structpb.NewStringValue("hi"), "proj:realm")
		AbsorbInline(dSrc, ref)

		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl:    proto.String(URL[*structpb.Value]()),
			Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
			OmitReason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED.Enum().Enum(),
			Realm:      proto.String("proj:realm"),
		}.Build(), ref)
	})

	t.Run(`outboard_noaccess`, func(t *testing.T) {
		t.Parallel()
		dSrc := SimpleDataSource{}

		ref := MustInline(structpb.NewStringValue("hi"), "proj:realm")
		AbsorbInline(dSrc, ref)

		Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)

		assert.Match(t, orchestratorpb.ValueRef_builder{
			TypeUrl:    proto.String(URL[*structpb.Value]()),
			OmitReason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS.Enum(),
			Realm:      proto.String("proj:realm"),
		}.Build(), ref)
	})
}
