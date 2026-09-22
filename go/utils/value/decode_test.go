// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"cmp"
	"slices"
	"strings"
	"testing"

	gocmp "github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/wrapperspb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestDecode(t *testing.T) {
	t.Parallel()

	t.Run(`ok_inline_binary`, func(t *testing.T) {
		t.Parallel()

		vref := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		sval, err := Decode[*structpb.Value](nil, vref)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if diff := gocmp.Diff(structpb.NewStringValue("hi"), sval, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`ok_source`, func(t *testing.T) {
		t.Parallel()

		vref := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		dSrc := SimpleDataSource{}
		AbsorbInline(dSrc, vref)

		if !vref.HasDigest() {
			t.Errorf("expected vref.HasDigest() to be true")
		}

		sval, err := Decode[*structpb.Value](dSrc, vref)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if diff := gocmp.Diff(structpb.NewStringValue("hi"), sval, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`ok_source_json`, func(t *testing.T) {
		t.Parallel()

		vref := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		dSrc := SimpleDataSource{}
		AbsorbAsJSON(dSrc, vref, protojson.MarshalOptions{})

		if !vref.HasDigest() {
			t.Errorf("expected vref.HasDigest() to be true")
		}
		if !dSrc.Retrieve(Digest(vref.GetDigest())).HasJson() {
			t.Errorf("expected dSrc entry to have JSON")
		}

		sval, err := Decode[*structpb.Value](dSrc, vref)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if diff := gocmp.Diff(structpb.NewStringValue("hi"), sval, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`missing`, func(t *testing.T) {
		t.Parallel()

		vref := orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Digest:  proto.String("bogus"),
		}.Build()

		dSrc := SimpleDataSource{}

		sval, err := Decode[*structpb.Value](dSrc, vref)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if sval != nil {
			t.Errorf("expected nil sval, got %v", sval)
		}
	})

	t.Run(`mismatch`, func(t *testing.T) {
		t.Parallel()

		vref := orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*emptypb.Empty]()),
			Digest:  proto.String("bogus"),
		}.Build()

		dSrc := SimpleDataSource{}

		_, err := Decode[*structpb.Value](dSrc, vref)
		if err == nil || !strings.Contains(err.Error(), "mismatched types") {
			t.Fatalf("expected error containing %q, got %v", "mismatched types", err)
		}
	})
}

func TestLookup(t *testing.T) {
	t.Parallel()

	var options []*orchestratorpb.ValueRef

	options, _ = SetByTypeIn(options, MustInline(&emptypb.Empty{}, "proj:realm"))
	options, _ = SetByTypeIn(options, MustInline(structpb.NewStringValue("hey"), "proj:realm"))
	options, _ = SetByTypeIn(options, MustInline(wrapperspb.UInt32(100), "proj:realm"))
	options, _ = SetByTypeIn(options, MustInline(wrapperspb.Bool(true), "proj:realm"))

	dSrc := SimpleDataSource{}
	AbsorbInline(dSrc, options[0]) // bool

	valGot, err := Lookup[*structpb.Value](dSrc, options)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if diff := gocmp.Diff(structpb.NewStringValue("hey"), valGot, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	boolGot, err := Lookup[*wrapperspb.BoolValue](dSrc, options)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if diff := gocmp.Diff(wrapperspb.Bool(true), boolGot, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	missing, err := Lookup[*wrapperspb.StringValue](dSrc, options)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if missing != nil {
		t.Errorf("expected nil missing, got %v", missing)
	}
}

func TestFind(t *testing.T) {
	t.Parallel()

	options := []*orchestratorpb.ValueRef{
		MustInline(&emptypb.Empty{}, "proj:realm"),
		MustInline(structpb.NewStringValue("hey"), "proj:realm"),
		MustInline(wrapperspb.UInt32(100), "proj:realm"),
		MustInline(wrapperspb.Bool(true), "proj:realm"),

		MustInline(&emptypb.Empty{}, "proj:other_realm"),
		MustInline(wrapperspb.UInt32(100), "proj:other_realm"),
	}
	Omit(options[0], orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)
	Omit(options[len(options)-1], orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)

	slices.SortStableFunc(options, func(a, b *orchestratorpb.ValueRef) int {
		return cmp.Compare(a.GetTypeUrl(), b.GetTypeUrl())
	})

	for _, opt := range options {
		t.Log(opt)
	}

	dSrc := SimpleDataSource{}
	AbsorbInline(dSrc, options[0]) // bool

	valGot := Find(options, URL[*structpb.Value]())
	if diff := gocmp.Diff(MustInline(structpb.NewStringValue("hey"), "proj:realm"), valGot, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	boolGot := Find(options, URL[*wrapperspb.BoolValue]())
	if diff := gocmp.Diff(options[0], boolGot, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	missing := Find(options, URL[*wrapperspb.StringValue]())
	if missing != nil {
		t.Errorf("expected nil missing, got %v", missing)
	}

	emptyGot := Find(options, URL[*emptypb.Empty]())
	if diff := gocmp.Diff(MustInline(&emptypb.Empty{}, "proj:other_realm"), emptyGot, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}
}

func TestResults(t *testing.T) {
	t.Parallel()

	sortedData := func(refs ...*orchestratorpb.ValueRef) []*orchestratorpb.ValueRef {
		ret := make([]*orchestratorpb.ValueRef, 0, len(refs))
		for _, ref := range refs {
			ok := false
			ret, ok = AddByTypeIn(ret, ref)
			if !ok {
				t.Errorf("expected AddByTypeIn to succeed")
			}
		}
		return ret
	}

	check := orchestratorpb.Check_builder{
		Results: []*orchestratorpb.Check_Result{
			orchestratorpb.Check_Result_builder{
				Data: sortedData(
					MustInline(&emptypb.Empty{}, ""),
					MustInline(wrapperspb.Bool(true), ""),
					MustInline(wrapperspb.String("hey"), ""),
				),
			}.Build(),
			orchestratorpb.Check_Result_builder{
				Data: sortedData(
					MustInline(&emptypb.Empty{}, ""),
					MustInline(wrapperspb.String("norp"), ""),
				),
			}.Build(),
			orchestratorpb.Check_Result_builder{}.Build(),
			orchestratorpb.Check_Result_builder{
				Data: sortedData(
					MustInline(&emptypb.Empty{}, ""),
					MustInline(wrapperspb.Bool(false), ""),
					MustInline(wrapperspb.String("dorp"), ""),
				),
			}.Build(),
		},
	}.Build()

	emptyRslts, err := Results[*emptypb.Empty](nil, check)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(emptyRslts) != 3 {
		t.Errorf("expected length 3, got %d: %v", len(emptyRslts), emptyRslts)
	}

	boolRslts, err := Results[*wrapperspb.BoolValue](nil, check)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	wantBools := []*wrapperspb.BoolValue{
		wrapperspb.Bool(true),
		wrapperspb.Bool(false),
	}
	if diff := gocmp.Diff(wantBools, boolRslts, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	strResults, err := Results[*wrapperspb.StringValue](nil, check)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	wantStrs := []*wrapperspb.StringValue{
		wrapperspb.String("hey"),
		wrapperspb.String("norp"),
		wrapperspb.String("dorp"),
	}
	if diff := gocmp.Diff(wantStrs, strResults, protocmp.Transform()); diff != "" {
		t.Errorf("mismatch (-want +got):\n%s", diff)
	}

	intResults, err := Results[*wrapperspb.Int32Value](nil, check)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(intResults) != 0 {
		t.Errorf("expected empty, got %v", intResults)
	}
}
