// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"slices"
	"strings"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestOmit(t *testing.T) {
	t.Parallel()

	sampleTags := []*orchestratorpb.Tag{
		orchestratorpb.Tag_builder{
			Key: proto.String("test"),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String("val"),
				}.Build(),
			},
		}.Build(),
	}

	inlineRef := func() *orchestratorpb.ValueRef {
		ref := MustInline(structpb.NewStringValue("hi"), "proj:realm")
		ref.SetTags(slices.Clone(sampleTags))
		return ref
	}

	outboardRef := func() *orchestratorpb.ValueRef {
		ref := inlineRef()
		AbsorbInline(SimpleDataSource{}, ref)
		return ref
	}

	cases := []struct {
		name       string
		ref        *orchestratorpb.ValueRef
		reason     orchestratorpb.OmitReason
		want       *orchestratorpb.ValueRef
		panicMatch string
	}{
		{
			name:   "unwanted+inline_data:keeps_digest",
			ref:    inlineRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED.Enum(),
				Realm:      proto.String("proj:realm"),
				Tags:       sampleTags,
			}.Build(),
		},
		{
			name:   "no_access+inline_data:drops_data",
			ref:    inlineRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS.Enum(),
				Realm:      proto.String("proj:realm"),
			}.Build(),
		},
		{
			name:   "missing+inline_data:keeps_digest",
			ref:    inlineRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_MISSING,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				Inline:     MustInline(structpb.NewStringValue("hi"), "proj:realm").GetInline(),
				Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_MISSING.Enum(),
				Realm:      proto.String("proj:realm"),
				Tags:       sampleTags,
			}.Build(),
		},
		{
			name:   "unwanted+digest:keeps_digest",
			ref:    outboardRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_UNWANTED.Enum(),
				Realm:      proto.String("proj:realm"),
				Tags:       sampleTags,
			}.Build(),
		},
		{
			name:   "no_access+digest:keeps_digest",
			ref:    outboardRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS.Enum(),
				Realm:      proto.String("proj:realm"),
			}.Build(),
		},
		{
			name:   "missing+digest:keeps_digest",
			ref:    outboardRef(),
			reason: orchestratorpb.OmitReason_OMIT_REASON_MISSING,
			want: orchestratorpb.ValueRef_builder{
				TypeUrl:    proto.String(URL[*structpb.Value]()),
				Digest:     proto.String("E4Va4xxp3BGN61fY0u4azK_FAF7_dA4-X58V7IkJrsgxAQ"),
				OmitReason: orchestratorpb.OmitReason_OMIT_REASON_MISSING.Enum(),
				Realm:      proto.String("proj:realm"),
				Tags:       sampleTags,
			}.Build(),
		},
		{
			name:       "unknown:panics",
			ref:        inlineRef(),
			reason:     orchestratorpb.OmitReason_OMIT_REASON_UNKNOWN,
			panicMatch: "unknown OmitReason",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			ref := proto.Clone(tc.ref).(*orchestratorpb.ValueRef)

			if tc.panicMatch != "" {
				defer func() {
					r := recover()
					if r == nil || !strings.Contains(fmt.Sprint(r), tc.panicMatch) {
						t.Errorf("expected panic containing %q, got: %v", tc.panicMatch, r)
					}
				}()
				Omit(ref, tc.reason)
				return
			}

			Omit(ref, tc.reason)
			if diff := cmp.Diff(tc.want, ref, protocmp.Transform()); diff != "" {
				t.Errorf("mismatch (-want +got):\n%s", diff)
			}
		})
	}
}
