// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package tags

import (
	"iter"
	"maps"
	"slices"
	"strings"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protodesc"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/reflect/protoregistry"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/descriptorpb"
	"google.golang.org/protobuf/types/dynamicpb"
	"google.golang.org/protobuf/types/known/emptypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	tagpb "go.chromium.org/turboci/proto/go/tag"
	testingtagspb "go.chromium.org/turboci/proto/go/testing/tags"
	tagsforvectorspb "go.chromium.org/turboci/proto/go/testing/vectors/tags/tags_for"
	"go.chromium.org/turboci/proto/go/utils/internal/test_vector"
)

var cmpOpts = []cmp.Option{
	protocmp.Transform(),
	cmp.AllowUnexported(
		Tag{},
		perValueState{},
	),
}

func TestTagsFor(t *testing.T) {
	t.Parallel()

	// Note we construct a completely separate descriptor pool using raw binary
	// descriptors embedded into the binary. This simulates "normal" dynamic
	// descriptor pools. We shouldn't directly reuse MessageDescriptor already
	// present in the built-in registry, since it may have ties to other built-in
	// descriptors, and then we'll be testing something weird, not truly dynamic
	// descriptor pools.
	dynreg := &protoregistry.Files{}
	for _, exemplar := range []proto.Message{
		// Note: order matters - need to register leafs of the dep graph first.
		// Also need just one representative message per *.proto file.
		&descriptorpb.FileDescriptorProto{},
		&emptypb.Empty{},
		&tagpb.Tag{},
		&testingtagspb.MyMessage{},
		&orchestratorpb.Tag{},
		&tagsforvectorspb.TagsFor{},
	} {
		path := exemplar.ProtoReflect().Descriptor().ParentFile().Path()
		fd, err := protoregistry.GlobalFiles.FindFileByPath(path)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		fdp := protodesc.ToFileDescriptorProto(fd)
		fd, err = protodesc.NewFile(fdp, dynreg)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		err = dynreg.RegisterFile(fd)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
	}

	test_vector.Run(t, _TAGS_FOR_VECTORS, func(t *testing.T, tc *tagsforvectorspb.TagsFor) {
		var msg proto.Message
		switch m := tc.GetInput(); m.WhichMsg() {
		case tagsforvectorspb.TagsFor_Input_My_case:
			msg = m.GetMy()
		case tagsforvectorspb.TagsFor_Input_Complex_case:
			msg = m.GetComplex()
		case tagsforvectorspb.TagsFor_Input_UnsupportedKind_case:
			msg = m.GetUnsupportedKind()
		case tagsforvectorspb.TagsFor_Input_Recursive_case:
			msg = m.GetRecursive()
		case tagsforvectorspb.TagsFor_Input_RecursiveUntagged_case:
			msg = m.GetRecursiveUntagged()
		case tagsforvectorspb.TagsFor_Input_MutualA_case:
			msg = m.GetMutualA()
		case tagsforvectorspb.TagsFor_Input_MutualB_case:
			msg = m.GetMutualB()
		case tagsforvectorspb.TagsFor_Input_MutualUntaggedA_case:
			msg = m.GetMutualUntaggedA()
		case tagsforvectorspb.TagsFor_Input_MutualUntaggedB_case:
			msg = m.GetMutualUntaggedB()
		case tagsforvectorspb.TagsFor_Input_LoopA_case:
			msg = m.GetLoopA()
		case tagsforvectorspb.TagsFor_Input_LoopB_case:
			msg = m.GetLoopB()
		case tagsforvectorspb.TagsFor_Input_LoopC_case:
			msg = m.GetLoopC()
		case tagsforvectorspb.TagsFor_Input_LoopD_case:
			msg = m.GetLoopD()
		case tagsforvectorspb.TagsFor_Input_Empty_case:
			msg = m.GetEmpty()
		default:
			// default to typed nil MyMessage.
			msg = (*testingtagspb.MyMessage)(nil)
		}

		// Construct a dynamicpb counterpart of `msg`.
		blob, err := proto.Marshal(msg)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		desc, err := dynreg.FindDescriptorByName(msg.ProtoReflect().Descriptor().FullName())
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		dyn := dynamicpb.NewMessage(desc.(protoreflect.MessageDescriptor))
		err = proto.Unmarshal(blob, dyn)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		for _, subcase := range []struct {
			name string
			msg  proto.Message
		}{
			{name: "static desc pool", msg: msg},
			{name: "dynamic desc pool", msg: dyn},
		} {
			t.Run(subcase.name, func(t *testing.T) {
				t.Parallel()

				tags, err := ForMessage(subcase.msg)
				output := tc.GetOutput()
				if output.HasError() {
					if err == nil || !strings.Contains(err.Error(), output.GetError()) {
						t.Fatalf("expected error containing %q, got %v", output.GetError(), err)
					}
				} else {
					if err != nil {
						t.Fatalf("unexpected error: %v", err)
					}
					if diff := cmp.Diff(output.GetTag(), tags.Proto(), cmpOpts...); diff != "" {
						t.Errorf("mismatch (-want +got):\n%s", diff)
					}
				}
			})
		}
	})
}

func TestHasValue(t *testing.T) {
	t.Parallel()

	tags, err := ForMessage(testingtagspb.ComplexMessage_builder{
		RepStr: []string{"c", "a", "b", "a"},
	}.Build())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	count, indexed := tags["testing.tags.ComplexMessage.rep_str"].HasValue("a")
	if count != 2 || indexed {
		t.Errorf("expected (2, false), got (%d, %v)", count, indexed)
	}
}

func TestTagsProto(t *testing.T) {
	t.Parallel()

	t.Run("basic", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:     "my.tag",
				Indexed: true,
				Strings: []string{"val1", "val1"},
				Ints:    []int{42},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key:     proto.String("my.tag"),
			Indexed: proto.Bool(true),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					Indexed:        proto.Bool(true),
					StrValue:       proto.String("val1"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Indexed:  proto.Bool(true),
					IntValue: proto.Int64(42),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("index_key_only", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:          "my.tag",
				Indexed:      true,
				IndexKeyOnly: true,
				Strings:      []string{"val1", "val1"},
				Ints:         []int{42},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key:     proto.String("my.tag"),
			Indexed: proto.Bool(true),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					StrValue:       proto.String("val1"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(42),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("strings_sorted_lexicographically", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key: "my.tag",
				Strings: []string{
					"zebra",
					"",
					"banana",
					"apple",
					"banana",
				},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key: proto.String("my.tag"),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String(""),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String("apple"),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					StrValue:       proto.String("banana"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String("zebra"),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("booleans_false_before_true", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:   "my.tag",
				Bools: []bool{true, false, true},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key: proto.String("my.tag"),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					BoolValue: proto.Bool(false),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					BoolValue:      proto.Bool(true),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("integers_sorted_numerically", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:  "my.tag",
				Ints: []int{42, -100, 0, 10, -100},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key: proto.String("my.tag"),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					IntValue:       proto.Int64(-100),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(0),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(10),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(42),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("mixed_type_ordering", func(t *testing.T) {
		t.Parallel()

		// StrValue < BoolValue < IntValue.
		protos := MakeMap(
			Builder{
				Key:     "my.tag",
				Ints:    []int{100, -5, 0},
				Strings: []string{"zebra", "apple", "apple"},
				Bools:   []bool{true, false},
			}.Build(),
		).Proto()
		if len(protos) != 1 {
			t.Fatalf("expected length 1, got %d: %v", len(protos), protos)
		}
		want := orchestratorpb.Tag_builder{
			Key: proto.String("my.tag"),
			Values: []*orchestratorpb.Tag_Value{
				// Strings first (lexicographical)
				orchestratorpb.Tag_Value_builder{
					StrValue:       proto.String("apple"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String("zebra"),
				}.Build(),
				// Booleans second (false before true)
				orchestratorpb.Tag_Value_builder{
					BoolValue: proto.Bool(false),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					BoolValue: proto.Bool(true),
				}.Build(),
				// Integers third (numerical)
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(-5),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(0),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(100),
				}.Build(),
			},
		}.Build()
		if diff := cmp.Diff(want, protos[0], cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})
}

func TestTagsForConvergence(t *testing.T) {
	// This test checks that our convergence process actually, you know,
	// converges. An earlier version had a mistake which resulted in the
	// convergence loop terminating after a single pass.
	//
	// This test sets up a D -> A -> B -> C -> D chain, which forces all four
	// messages into the toConverge set.
	//
	// Because Go iterates maps in a randomized order, it's POSSIBLE for the
	// buggy implementation to get lucky and visit these in reverse order (it's
	// about a 4% chance). We clear the pool and run the test 4 times to make the
	// odds of getting lucky vanishingly small.
	msg := testingtagspb.LoopMessageD_builder{
		Tagged: proto.String("d_root"),
		Deeper: testingtagspb.LoopMessageA_builder{
			Deeper: testingtagspb.LoopMessageB_builder{
				Deeper: testingtagspb.LoopMessageC_builder{
					Deeper: testingtagspb.LoopMessageD_builder{
						Tagged: proto.String("d_nested"),
					}.Build(),
				}.Build(),
			}.Build(),
		}.Build(),
	}.Build()

	want := MakeMap(
		Builder{
			Key:     "testing.tags.LoopMessageD.tagged",
			Strings: []string{"d_nested", "d_root"},
		}.Build(),
	)

	for range 10 {
		tagExtractorPoolMu.Lock()
		clear(tagExtractorPool)
		tagExtractorPoolMu.Unlock()

		tags, err := ForMessage(msg)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if diff := cmp.Diff(want, tags, cmpOpts...); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	}
}

func fieldTagsTestCase[M proto.Message](want map[string]*tagpb.Tag) (name string, tc func(t *testing.T)) {
	var zero M
	return string(zero.ProtoReflect().Descriptor().FullName()), func(t *testing.T) {
		t.Parallel()

		expectedFields := maps.Clone(want)
		for field, tag := range FieldTags[M] {
			name := string(field.FullName())
			want, ok := expectedFields[name]
			if !ok {
				t.Errorf("field %q was not expected", name)
				continue
			}
			if diff := cmp.Diff(want, tag, cmpOpts...); diff != "" {
				t.Errorf("mismatch for %q (-want +got):\n%s", name, diff)
			}
			delete(expectedFields, name)
		}
		if len(expectedFields) != 0 {
			t.Errorf("expectedFields not empty: %v", expectedFields)
		}
	}
}

func TestMetadata(t *testing.T) {
	t.Parallel()

	t.Run(fieldTagsTestCase[*testingtagspb.MyMessage](map[string]*tagpb.Tag{
		"testing.tags.MyMessage.tagged_field": {},
	}))

	t.Run(fieldTagsTestCase[*testingtagspb.ComplexMessage](map[string]*tagpb.Tag{
		"testing.tags.ComplexMessage.SubMessage.sub_tagged": tagpb.Tag_builder{
			AltKey: []string{"previous.package.name.Message.field"},
		}.Build(),
		"testing.tags.ComplexMessage.local_str": tagpb.Tag_builder{
			Indexed: proto.Bool(false),
		}.Build(),
		"testing.tags.ComplexMessage.workplan_str": tagpb.Tag_builder{
			Indexed: proto.Bool(true),
		}.Build(),
		"testing.tags.ComplexMessage.local_bool": tagpb.Tag_builder{
			Indexed:      proto.Bool(false),
			CaptureUnset: proto.Bool(true),
		}.Build(),
		"testing.tags.ComplexMessage.local_enum": tagpb.Tag_builder{
			Indexed: proto.Bool(false),
		}.Build(),
		"testing.tags.ComplexMessage.rep_str": tagpb.Tag_builder{
			Indexed: proto.Bool(false),
		}.Build(),
		"testing.tags.ComplexMessage.split_index": tagpb.Tag_builder{
			Indexed:      proto.Bool(true),
			IndexKeyOnly: proto.Bool(true),
		}.Build(),
		"testing.tags.ComplexMessage.explicit_presence_bool": tagpb.Tag_builder{
			CaptureUnset: proto.Bool(false),
		}.Build(),
	}))

	// Messages which are improperly tagged yield nothing.
	t.Run(fieldTagsTestCase[*testingtagspb.UnsupportedKindMessage](nil))

	t.Run(fieldTagsTestCase[*testingtagspb.RecursiveMessage](map[string]*tagpb.Tag{
		"testing.tags.RecursiveMessage.tagged": {},
	}))

	t.Run(fieldTagsTestCase[*testingtagspb.LoopMessageD](map[string]*tagpb.Tag{
		"testing.tags.LoopMessageD.tagged": {},
	}))
}

func intTagValue(v int64, count uint32) *orchestratorpb.Tag_Value {
	if count <= 0 {
		panic("count must be > 0")
	}
	b := orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(v)}
	if count > 1 {
		b.DuplicateCount = proto.Uint32(count - 1)
	}
	return b.Build()
}

func strTagValue(v string, count uint32) *orchestratorpb.Tag_Value {
	if count <= 0 {
		panic("count must be > 0")
	}
	b := orchestratorpb.Tag_Value_builder{StrValue: proto.String(v)}
	if count > 1 {
		b.DuplicateCount = proto.Uint32(count - 1)
	}
	return b.Build()
}

func boolTagValue(v bool, count uint32) *orchestratorpb.Tag_Value {
	if count <= 0 {
		panic("count must be > 0")
	}
	b := orchestratorpb.Tag_Value_builder{BoolValue: proto.Bool(v)}
	if count > 1 {
		b.DuplicateCount = proto.Uint32(count - 1)
	}
	return b.Build()
}

func makeTagProto(key string, vals ...*orchestratorpb.Tag_Value) *orchestratorpb.Tag {
	return orchestratorpb.Tag_builder{
		Key:    proto.String(key),
		Values: vals,
	}.Build()
}

func asIndexedTag(tag *orchestratorpb.Tag) *orchestratorpb.Tag {
	c := proto.CloneOf(tag)
	c.SetIndexed(true)
	return c
}

func makeValueRef(tags ...*orchestratorpb.Tag) *orchestratorpb.ValueRef {
	return orchestratorpb.ValueRef_builder{Tags: tags}.Build()
}

func TestFromValueRefs(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name string
		refs iter.Seq[*orchestratorpb.ValueRef]
		want Map
	}{
		{
			name: "homogeneous",
			refs: slices.Values([]*orchestratorpb.ValueRef{
				makeValueRef(
					makeTagProto("attempt_num", intTagValue(10, 1), intTagValue(20, 3)),
					makeTagProto("env", strTagValue("prod", 2)),
				),
				makeValueRef(
					makeTagProto("attempt_num", intTagValue(20, 2), intTagValue(30, 1)),
					makeTagProto("flaky", boolTagValue(true, 4), boolTagValue(false, 1)),
				),
			}),
			want: MakeMap(
				Builder{Key: "attempt_num", Ints: []int{10, 20, 20, 20, 20, 20, 30}}.Build(),
				Builder{Key: "env", Strings: []string{"prod", "prod"}}.Build(),
				Builder{Key: "flaky", Bools: []bool{false, true, true, true, true}}.Build(),
			),
		},
		{
			name: "mixed_types",
			refs: slices.Values([]*orchestratorpb.ValueRef{
				makeValueRef(makeTagProto("mixed", intTagValue(1, 1), strTagValue("one", 3), intTagValue(2, 5))),
				makeValueRef(makeTagProto("mixed", strTagValue("two", 1), strTagValue("one", 1))),
			}),
			want: MakeMap(
				Builder{
					Key:     "mixed",
					Ints:    []int{1, 2, 2, 2, 2, 2},
					Strings: []string{"one", "one", "one", "one", "two"},
				}.Build(),
			),
		},
		{
			name: "unset_data_and_presence_merges",
			refs: slices.Values([]*orchestratorpb.ValueRef{
				makeValueRef(
					makeTagProto("presence_only"),
					asIndexedTag(makeTagProto("presence_only_indexed")),
					makeTagProto(
						"only_unset_data",
						&orchestratorpb.Tag_Value{},
					),
					makeTagProto("partially_set", &orchestratorpb.Tag_Value{}, strTagValue("valid", 2)),
					asIndexedTag(makeTagProto("presence_then_value")),
					makeTagProto("value_then_presence", strTagValue("v1", 1)),
				),
				makeValueRef(
					makeTagProto("presence_then_value", strTagValue("v1", 2)),
					asIndexedTag(makeTagProto("value_then_presence")),
				),
			}),
			want: Map{
				"presence_only":         &Tag{},
				"presence_only_indexed": &Tag{indexed: true},
				"only_unset_data":       &Tag{},
				"partially_set": MakeMap(
					Builder{Key: "partially_set", Strings: []string{"valid", "valid"}}.Build(),
				)["partially_set"],
				"presence_then_value": MakeMap(
					Builder{Key: "presence_then_value", IndexKeyOnly: true, Strings: []string{"v1", "v1"}}.Build(),
				)["presence_then_value"],
				"value_then_presence": MakeMap(
					Builder{Key: "value_then_presence", IndexKeyOnly: true, Strings: []string{"v1"}}.Build(),
				)["value_then_presence"],
			},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			got := FromValueRefs(tc.refs)
			if diff := cmp.Diff(tc.want, got, cmpOpts...); diff != "" {
				t.Errorf("FromValueRefs() mismatch (-want +got):\n%s", diff)
			}
		})
	}
}

func TestAddValueRefs(t *testing.T) {
	t.Parallel()

	m := Map{}
	m.AddValueRefs(slices.Values([]*orchestratorpb.ValueRef{
		makeValueRef(
			makeTagProto("k", strTagValue("b", 1), intTagValue(2, 2)),
			asIndexedTag(makeTagProto("presence_then_val")),
			makeTagProto("val_then_presence", intTagValue(7, 1)),
		),
	}))
	m.AddValueRefs(slices.Values([]*orchestratorpb.ValueRef{
		makeValueRef(
			makeTagProto("k", strTagValue("a", 2), intTagValue(2, 1), boolTagValue(true, 1)),
			makeTagProto("presence_then_val", intTagValue(7, 1)),
			asIndexedTag(makeTagProto("val_then_presence")),
		),
	}))

	want := MakeMap(
		Builder{
			Key:     "k",
			Strings: []string{"a", "a", "b"},
			Ints:    []int{2, 2, 2},
			Bools:   []bool{true},
		}.Build(),
		Builder{
			Key:          "presence_then_val",
			IndexKeyOnly: true,
			Ints:         []int{7},
		}.Build(),
		Builder{
			Key:          "val_then_presence",
			IndexKeyOnly: true,
			Ints:         []int{7},
		}.Build(),
	)
	if diff := cmp.Diff(want, m, cmpOpts...); diff != "" {
		t.Errorf("AddValueRefs() mismatch (-want +got):\n%s", diff)
	}
}

func TestMapAndTagQueries(t *testing.T) {
	t.Parallel()

	m := FromValueRefs(slices.Values([]*orchestratorpb.ValueRef{
		makeValueRef(
			makeTagProto("mixed", intTagValue(10, 2), intTagValue(-5, 1), strTagValue("b", 1), strTagValue("a", 3), boolTagValue(true, 2), boolTagValue(false, 1)),
			makeTagProto("ints_only", intTagValue(3, 1), intTagValue(1, 2)),
			makeTagProto("strs_only", strTagValue("z", 1), strTagValue("a", 2)),
			makeTagProto("bools_only", boolTagValue(true, 1), boolTagValue(false, 2)),
			makeTagProto("presence_only"),
		),
		makeValueRef(
			makeTagProto(
				"mixed",
				orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(10), Indexed: proto.Bool(true)}.Build(),
				strTagValue("a", 1),
			),
		),
	}))

	for _, tc := range []struct {
		key         string
		wantPresent bool
		wantInts    []int64
		wantStrings []string
		wantBools   []bool
	}{
		{
			key:         "mixed",
			wantPresent: true,
			wantInts:    []int64{-5, 10, 10, 10},
			wantStrings: []string{"a", "a", "a", "a", "b"},
			wantBools:   []bool{false, true, true},
		},
		{
			key:         "ints_only",
			wantPresent: true,
			wantInts:    []int64{1, 1, 3},
			wantStrings: []string{},
			wantBools:   []bool{},
		},
		{
			key:         "strs_only",
			wantPresent: true,
			wantInts:    []int64{},
			wantStrings: []string{"a", "a", "z"},
			wantBools:   []bool{},
		},
		{
			key:         "bools_only",
			wantPresent: true,
			wantInts:    []int64{},
			wantStrings: []string{},
			wantBools:   []bool{false, false, true},
		},
		{
			key:         "presence_only",
			wantPresent: true,
			wantInts:    []int64{},
			wantStrings: []string{},
			wantBools:   []bool{},
		},
		{
			key:         "missing",
			wantPresent: false,
			wantInts:    []int64{},
			wantStrings: []string{},
			wantBools:   []bool{},
		},
	} {
		t.Run(tc.key, func(t *testing.T) {
			t.Parallel()
			if gotPresent := m[tc.key] != nil; gotPresent != tc.wantPresent {
				t.Errorf("m[%q] != nil = %v, want %v", tc.key, gotPresent, tc.wantPresent)
			}
			if got := m.IntValues(tc.key); got == nil || !slices.Equal(got, tc.wantInts) {
				t.Errorf("m.IntValues(%q) = %#v, want %#v", tc.key, got, tc.wantInts)
			}
			if got := m.StringValues(tc.key); got == nil || !slices.Equal(got, tc.wantStrings) {
				t.Errorf("m.StringValues(%q) = %#v, want %#v", tc.key, got, tc.wantStrings)
			}
			if got := m.BoolValues(tc.key); got == nil || !slices.Equal(got, tc.wantBools) {
				t.Errorf("m.BoolValues(%q) = %#v, want %#v", tc.key, got, tc.wantBools)
			}
		})
	}

	t.Run("nil_map", func(t *testing.T) {
		t.Parallel()
		var nilMap Map
		if got := nilMap.IntValues("k"); got == nil || len(got) != 0 {
			t.Errorf("nilMap.IntValues(%q) = %#v, want []int64{}", "k", got)
		}
		if got := nilMap.StringValues("k"); got == nil || len(got) != 0 {
			t.Errorf("nilMap.StringValues(%q) = %#v, want []string{}", "k", got)
		}
		if got := nilMap.BoolValues("k"); got == nil || len(got) != 0 {
			t.Errorf("nilMap.BoolValues(%q) = %#v, want []bool{}", "k", got)
		}
	})

	for _, tc := range []struct {
		name        string
		key         string
		val         any
		wantCount   uint32
		wantIndexed bool
	}{
		{"has_value_int_indexed", "mixed", int64(10), 3, true},
		{"has_value_int_unindexed", "mixed", int64(-5), 1, false},
		{"has_value_int_missing", "mixed", int64(99), 0, false},
		{"has_value_str_repeated", "mixed", "a", 4, false},
		{"has_value_str_single", "mixed", "b", 1, false},
		{"has_value_str_missing", "mixed", "c", 0, false},
		{"has_value_bool_true", "mixed", true, 2, false},
		{"has_value_bool_false", "mixed", false, 1, false},
		{"has_value_presence_only", "presence_only", "a", 0, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			gotCount, gotIndexed := m[tc.key].HasValue(tc.val)
			if gotCount != tc.wantCount || gotIndexed != tc.wantIndexed {
				t.Errorf("m[%q].HasValue(%v) = (%d, %v), want (%d, %v)", tc.key, tc.val, gotCount, gotIndexed, tc.wantCount, tc.wantIndexed)
			}
		})
	}
}
