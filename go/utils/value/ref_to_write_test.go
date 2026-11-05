// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"go.chromium.org/turboci/proto/go/utils/tags"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/durationpb"
	"google.golang.org/protobuf/types/known/structpb"
)

func TestRefToWrite(t *testing.T) {
	t.Parallel()

	realm := "proj:somerealm"

	dat1 := MustWrite(durationpb.New(10*time.Second), realm)
	dat2 := MustInline(structpb.NewStringValue("hi"), realm)

	tags := tags.MakeMap(
		tags.Builder{Key: "some.tag"}.Build(),
	).Proto()

	source := SimpleDataSource{}
	source.Intern(ComputeDigest(dat1.GetData()), orchestratorpb.ValueData_builder{
		Binary: dat1.GetData(),
	}.Build())
	source.Intern("badc0ffee", orchestratorpb.ValueData_builder{
		Json: orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String(URL[*structpb.ListValue]()),
			Value:   proto.String("I am a teapot"),
		}.Build(),
	}.Build())
	AbsorbAsJSON(source, dat2, protojson.MarshalOptions{})

	tests := []struct {
		name     string
		ref      func(ref *orchestratorpb.ValueRef)
		want     func(vw *orchestratorpb.ValueWrite)
		wantErr  string
		wantOmit orchestratorpb.OmitReason
	}{
		{
			name: "ok - inline",
			ref: func(ref *orchestratorpb.ValueRef) {
				ref.SetDigest(string(ComputeDigest(dat1.GetData())))
				ref.SetInline(dat1.GetData())
				ref.SetTags(tags)
			},
			want: func(vw *orchestratorpb.ValueWrite) {
				proto.Merge(vw, dat1)
				vw.SetTags(tags)
			},
		},

		{
			name: "ok - outline",
			ref: func(ref *orchestratorpb.ValueRef) {
				ref.SetDigest(string(ComputeDigest(dat1.GetData())))
				ref.SetTags(tags)
			},
			want: func(vw *orchestratorpb.ValueWrite) {
				proto.Merge(vw, dat1)
				vw.SetTags(tags)
			},
		},

		{
			name: "ok - outline JSON",
			ref: func(ref *orchestratorpb.ValueRef) {
				proto.Merge(ref, dat2)
				ref.SetTags(tags)
			},
			want: func(vw *orchestratorpb.ValueWrite) {
				proto.Merge(vw, MustWrite(structpb.NewStringValue("hi"), realm))
				vw.SetTags(tags)
			},
		},

		{
			name: "bad - omitted",
			ref: func(ref *orchestratorpb.ValueRef) {
				Omit(ref, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)
			},
			wantErr:  "data is omitted",
			wantOmit: orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS,
		},

		{
			name: "bad - missing type_url",
			ref: func(ref *orchestratorpb.ValueRef) {
				ref.SetTypeUrl(TypePrefix + "potato.Cannon")
			},
			wantErr: "error getting descriptor",
		},

		{
			name: "bad - corrupt JSON",
			ref: func(ref *orchestratorpb.ValueRef) {
				ref.SetTypeUrl(URL[*structpb.ListValue]())
				ref.SetDigest("badc0ffee")
			},
			wantErr: "error unmarshaling JSON",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			ref := &orchestratorpb.ValueRef{}
			ref.SetRealm(realm)
			if tc.ref != nil {
				tc.ref(ref)
			}

			vw, err := RefToWrite(source, ref)
			if err != nil {
				if tc.wantErr == "" || !strings.Contains(err.Error(), tc.wantErr) {
					t.Errorf("unexpected error: %s", err)
					t.Errorf("wanted: %s", tc.wantErr)
				}
				if tc.wantOmit != 0 {
					var omitErr OmittedDataError
					if !errors.As(err, &omitErr) {
						t.Errorf("expected OmittedDataError, got %T: %v", err, err)
					} else if omitErr.OmitReason != tc.wantOmit {
						t.Errorf("got OmitReason %v, want %v", omitErr.OmitReason, tc.wantOmit)
					}
				}
			} else if tc.wantErr != "" {
				t.Errorf("expected error containing %q, got nil", tc.wantErr)
			} else {
				want := &orchestratorpb.ValueWrite{}
				if tc.want != nil {
					tc.want(want)
				}
				if diff := cmp.Diff(vw, want, protocmp.Transform()); diff != "" {
					t.Errorf("unexpected diff: %s", diff)
				}
			}
		})
	}
}
