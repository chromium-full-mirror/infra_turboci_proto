// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"math"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/encoding/protowire"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestHasUnknownFields(t *testing.T) {
	t.Parallel()

	t.Run(`basic`, func(t *testing.T) {
		t.Parallel()

		buf := protowire.AppendTag(nil, 1, protowire.VarintType)
		buf = protowire.AppendVarint(buf, 12345)

		e := &emptypb.Empty{}

		if err := proto.Unmarshal(buf, e); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if !hasUnknownFields(e.ProtoReflect()) {
			t.Errorf("expected hasUnknownFields to be true")
		}
	})

	t.Run(`list`, func(t *testing.T) {
		t.Parallel()

		// inner is a structpb.Value w/ number_value(1.234) plus 20:varint(100)
		inner := protowire.AppendTag(nil, 2, protowire.Fixed64Type)
		inner = protowire.AppendFixed64(inner, math.Float64bits(1.234))
		inner = protowire.AppendTag(inner, 20, protowire.VarintType)
		inner = protowire.AppendVarint(inner, 100)

		// outer is a structpb.List
		outer := protowire.AppendTag(nil, 1, protowire.BytesType)
		outer = protowire.AppendBytes(outer, inner)

		l := &structpb.ListValue{}
		if err := proto.Unmarshal(outer, l); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		newList, err := structpb.NewList([]any{1.234})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if diff := cmp.Diff(newList, l, protocmp.Transform(), protocmp.IgnoreUnknown()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}

		if !hasUnknownFields(l.ProtoReflect()) {
			t.Errorf("expected hasUnknownFields to be true")
		}
	})

	t.Run(`map`, func(t *testing.T) {
		t.Parallel()

		// inner is a structpb.Value w/ number_value(1.234) plus 20:varint(100)
		inner := protowire.AppendTag(nil, 2, protowire.Fixed64Type)
		inner = protowire.AppendFixed64(inner, math.Float64bits(1.234))
		inner = protowire.AppendTag(inner, 20, protowire.VarintType)
		inner = protowire.AppendVarint(inner, 100)

		// mapVal is the implied map entry message
		mapVal := protowire.AppendTag(nil, 1, protowire.BytesType)
		mapVal = protowire.AppendBytes(mapVal, []byte("key"))
		mapVal = protowire.AppendTag(mapVal, 2, protowire.BytesType)
		mapVal = protowire.AppendBytes(mapVal, inner)

		// outer is a structpb.Struct
		outer := protowire.AppendTag(nil, 1, protowire.BytesType)
		outer = protowire.AppendBytes(outer, mapVal)

		s := &structpb.Struct{}
		if err := proto.Unmarshal(outer, s); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		newStruct, err := structpb.NewStruct(map[string]any{"key": 1.234})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if diff := cmp.Diff(newStruct, s, protocmp.Transform(), protocmp.IgnoreUnknown()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}

		if !hasUnknownFields(s.ProtoReflect()) {
			t.Errorf("expected hasUnknownFields to be true")
		}
	})

	t.Run(`nested`, func(t *testing.T) {
		t.Parallel()

		// inner is a structpb.Value w/ number_value(1.234) plus 20:varint(100)
		inner := protowire.AppendTag(nil, 2, protowire.Fixed64Type)
		inner = protowire.AppendFixed64(inner, math.Float64bits(1.234))
		inner = protowire.AppendTag(inner, 20, protowire.VarintType)
		inner = protowire.AppendVarint(inner, 100)

		// mapVal is the implied map entry message
		mapVal := protowire.AppendTag(nil, 1, protowire.BytesType)
		mapVal = protowire.AppendBytes(mapVal, []byte("key"))
		mapVal = protowire.AppendTag(mapVal, 2, protowire.BytesType)
		mapVal = protowire.AppendBytes(mapVal, inner)

		// structVal is a structpb.Struct
		structVal := protowire.AppendTag(nil, 1, protowire.BytesType)
		structVal = protowire.AppendBytes(structVal, mapVal)

		// outer is a Value with the struct field set
		outer := protowire.AppendTag(nil, 5, protowire.BytesType)
		outer = protowire.AppendBytes(outer, structVal)

		v := &structpb.Value{}
		if err := proto.Unmarshal(outer, v); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		newStruct, err := structpb.NewStruct(map[string]any{"key": 1.234})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		val := structpb.NewStructValue(newStruct)
		if diff := cmp.Diff(val, v, protocmp.Transform(), protocmp.IgnoreUnknown()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}

		if !hasUnknownFields(v.ProtoReflect()) {
			t.Errorf("expected hasUnknownFields to be true")
		}
	})
}

func TestEnsureJSONInSource(t *testing.T) {
	t.Parallel()

	t.Run(`ok`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Value:   proto.String(`"hi"`),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(Digest(v.GetDigest())).GetJson(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`already_absorbed`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		AbsorbInline(dSrc, v)

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Value:   proto.String(`"hi"`),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(Digest(v.GetDigest())).GetJson(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`already_json`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(structpb.NewStringValue("hi"), "proj:realm")

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		// should be a no-op
		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String(URL[*structpb.Value]()),
			Value:   proto.String(`"hi"`),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(Digest(v.GetDigest())).GetJson(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`not_in_registry`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := orchestratorpb.ValueRef_builder{
			TypeUrl: proto.String(URL[*emptypb.Empty]()),
			Digest:  proto.String("superfake"),
		}.Build()

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})
		if len(dSrc) != 0 {
			t.Errorf("expected empty dSrc, got len %d", len(dSrc))
		}
	})

	t.Run(`unknown_fields`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(&emptypb.Empty{}, "proj:realm")

		raw, err := proto.Marshal(structpb.NewStringValue("hi"))
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		v.GetInline().Value = raw

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl:          proto.String(URL[*emptypb.Empty]()),
			Value:            proto.String("{}"),
			HasUnknownFields: proto.Bool(true),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(Digest(v.GetDigest())).GetJson(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`missing descriptor`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(&emptypb.Empty{}, "proj:realm")
		v.SetTypeUrl(TypePrefix + "fake.type.NoDescriptor")
		v.GetInline().TypeUrl = TypePrefix + "fake.type.NoDescriptor"
		rawData := proto.CloneOf(v.GetInline())

		dgst := ComputeDigest(v.GetInline())

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_builder{
			Binary:            rawData,
			ConversionFailure: orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_NO_DESCRIPTOR.Enum(),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(dgst), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run(`conversion failure sticky`, func(t *testing.T) {
		t.Parallel()

		dSrc := SimpleDataSource{}
		v := MustInline(&emptypb.Empty{}, "proj:realm")
		emptyInline := proto.CloneOf(v.GetInline())
		dgst := ComputeDigest(v.GetInline())

		AbsorbInline(dSrc, v)
		dSrc.Intern(dgst, orchestratorpb.ValueData_builder{
			Binary:            emptyInline,
			ConversionFailure: orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_NO_DESCRIPTOR.Enum(),
		}.Build())

		AbsorbAsJSON(dSrc, v, protojson.MarshalOptions{})

		want := orchestratorpb.ValueData_builder{
			Binary:            emptyInline,
			ConversionFailure: orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_NO_DESCRIPTOR.Enum(),
		}.Build()
		if diff := cmp.Diff(want, dSrc.Retrieve(dgst), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}

		// A second, unrelated, inline'd Empty.
		AbsorbAsJSON(dSrc, MustInline(&emptypb.Empty{}, "other:realm"), protojson.MarshalOptions{})

		if diff := cmp.Diff(want, dSrc.Retrieve(dgst), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})
}
