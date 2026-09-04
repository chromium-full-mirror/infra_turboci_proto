// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"strings"
	"testing"

	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"

	commonpb "go.chromium.org/turboci/proto/go/data/common/v1"
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestMakeTypeMatcher(t *testing.T) {
	t.Parallel()

	testCases := []struct {
		name string

		urls    []string
		wantErr string
		wantN   int

		matches []string
		rejects []string
	}{
		{
			name:    "empty",
			rejects: []string{"hi", URL[*emptypb.Empty]()},
		},
		{
			name: "static",
			urls: []string{
				URL[*emptypb.Empty](),
				URL[*structpb.Value](),
			},
			wantN: 2,
			matches: []string{
				URL[*emptypb.Empty](),
				URL[*structpb.Value](),
			},
			rejects: []string{
				"hi",
				URL[*structpb.ListValue](),
				// This will produce e.g. `google_protobuf_Empty`; if we don't
				// correctly escape the metachars in the regex, then our pattern for
				// `google.protobuf.Empty` would match accidentally.
				strings.ReplaceAll(URL[*emptypb.Empty](), ".", "_"),
			},
		},
		{
			name: "wildcard_package",
			urls: []string{
				URLPatternPackageOf[*structpb.Value](),
			},
			wantN: 1,
			matches: []string{
				URL[*structpb.Value](),
				URL[*structpb.ListValue](),
				URL[*structpb.Struct](),
				URL[*emptypb.Empty](),
			},
			rejects: []string{"hi", URL[*commonpb.DisplayMessage]()},
		},
		{
			name: "prefix_star",
			urls: []string{
				TypePrefix + "*",
			},
			wantN: 1,
			matches: []string{
				URL[*structpb.Value](),
				URL[*structpb.ListValue](),
				URL[*structpb.Struct](),
				URL[*emptypb.Empty](),
				URL[*commonpb.DisplayMessage](),
			},
			rejects: []string{"hi"},
		},
		{
			name: "bare_star",
			urls: []string{
				"*",
			},
			wantN: 1,
			matches: []string{
				URL[*structpb.Value](),
				URL[*structpb.ListValue](),
				URL[*structpb.Struct](),
				URL[*emptypb.Empty](),
				URL[*commonpb.DisplayMessage](),
				TypePrefix + "very.long.package.Spam",
				TypePrefix + "very.Cool",
				TypePrefix + "very.Cool",
				TypePrefix + "*",
			},
		},
		{
			name: "bad_prefix",
			urls: []string{
				"asdf*",
			},
			wantErr: "expected prefix",
		},
		{
			name: "bad_star",
			urls: []string{
				TypePrefix + "hello*",
			},
			wantErr: "may only be used in a suffix",
		},
		{
			name: "double_star",
			urls: []string{
				TypePrefix + "*hello.*",
			},
			wantErr: "multiple *",
		},
		{
			name: "normalized",
			urls: []string{
				TypePrefix + "very.long.package.*",
				TypePrefix + "very.Cool",
				TypePrefix + "very.long.*",
				TypePrefix + "very.long.package.Spam",
				TypePrefix + "very.Cool",
				TypePrefix + "very.Cool",
			},
			wantN: 2,
			matches: []string{
				TypePrefix + "very.long.Cooltype",
				TypePrefix + "very.Cool",
				TypePrefix + "very.long.package.OtherType",
			},
			rejects: []string{
				TypePrefix + "very.longpkg.Cooltype",
				TypePrefix + "very.Notcool",
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			matcher, err := MakeTypeMatcher(orchestratorpb.TypeSet_builder{
				TypeUrls: tc.urls,
			}.Build())
			if tc.wantErr != "" {
				assert.ErrLike(t, err, tc.wantErr)
				return
			}

			assert.Len(t, matcher.patterns, tc.wantN)

			assert.NoErr(t, err)

			for _, matchCandidate := range tc.matches {
				assert.True(t, matcher.Match(matchCandidate))
			}
			for _, rejectCandidate := range tc.rejects {
				assert.False(t, matcher.Match(rejectCandidate))
			}
		})
	}
}

func TestTypeSetBuilder(t *testing.T) {
	t.Parallel()

	t.Run(`empty`, func(t *testing.T) {
		t.Parallel()

		tb, err := TypeSetBuilder{}.Build()
		assert.NoErr(t, err)
		assert.Nil(t, tb)
	})

	t.Run(`fixed`, func(t *testing.T) {
		t.Parallel()

		tb, err := TypeSetBuilder{}.WithMessages(&emptypb.Empty{}, &structpb.Struct{}).Build()
		assert.NoErr(t, err)
		assert.Len(t, tb.GetTypeUrls(), 2)
	})

	t.Run(`normalized`, func(t *testing.T) {
		t.Parallel()

		tb, err := (TypeSetBuilder{}.
			WithMessages(&emptypb.Empty{}, &structpb.Struct{}).
			WithPackagesOf(&structpb.ListValue{}).
			Build())
		assert.NoErr(t, err)
		assert.Len(t, tb.GetTypeUrls(), 1)
		assert.Equal(t, TypePrefix+"google.protobuf.*", tb.GetTypeUrls()[0])
	})
}
