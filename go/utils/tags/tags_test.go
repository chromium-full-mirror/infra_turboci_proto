// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package tags

import (
	"maps"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protodesc"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/reflect/protoregistry"
	"google.golang.org/protobuf/types/dynamicpb"
	"google.golang.org/protobuf/types/known/emptypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	tagpb "go.chromium.org/turboci/proto/go/tag"
	testingtagspb "go.chromium.org/turboci/proto/go/testing/tags"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

const (
	node     = orchestratorpb.ReadScope_READ_SCOPE_NODE
	workPlan = orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN
)

func init() {
	assert.DefaultOptions = append(assert.DefaultOptions, cmp.AllowUnexported(
		Tag{},
		scopeCount{},
	))
}

func TestTagsFor(t *testing.T) {
	t.Parallel()

	// Note we construct a completely separate descriptor pool using raw
	// binary descriptors embedded into the binary. This simulates "normal"
	// dynamic descriptor pools. We shouldn't directly reuse MessageDescriptor
	// already present in the built-in registry, since it may have ties to other
	// built-in descriptors, and then we'll be testing something weird, not truly
	// dynamic descriptor pools.
	dynreg := &protoregistry.Files{}
	for _, path := range []string{
		// Note: order matters - need to register leafs of the dep graph first.
		"google/protobuf/descriptor.proto",
		"google/protobuf/empty.proto",
		"turboci/tag.proto",
		"testing/tags/demo.proto",
	} {
		fd, err := protoregistry.GlobalFiles.FindFileByPath(path)
		assert.NoErr(t, err)
		fdp := protodesc.ToFileDescriptorProto(fd)
		fd, err = protodesc.NewFile(fdp, dynreg)
		assert.NoErr(t, err)
		err = dynreg.RegisterFile(fd)
		assert.NoErr(t, err)
	}

	tests := []struct {
		name     string
		msg      proto.Message
		wantErr  string
		wantTags Map
		// extraAssert is called after comparing to wantTags to allow additional
		// assertions.
		extraAssert func(t *testing.T, tags Map)
	}{
		{
			name: "nil",
			msg:  (*testingtagspb.MyMessage)(nil),
		},
		{
			name: "Empty",
			msg:  &emptypb.Empty{},
		},
		{
			name: "MyMessage.untagged_field",
			msg: testingtagspb.MyMessage_builder{
				UntaggedField: proto.String("hello"),
			}.Build(),
		},
		{
			name: "MyMessage.tagged_field",
			msg: testingtagspb.MyMessage_builder{
				TaggedField: proto.String("hello"),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.MyMessage.tagged_field",
					Strings: []string{"hello"},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.local_str",
			msg: testingtagspb.ComplexMessage_builder{
				LocalStr: proto.String("foo"),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.ComplexMessage.local_str",
					Strings: []string{"foo"},
				}.Build(),

				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.workplan_str",
			msg: testingtagspb.ComplexMessage_builder{
				WorkplanStr: proto.String("foo"),
			}.Build(),
			wantTags: MakeMap(
				// because it's set to value_scope=NODE, both the key and value are
				// set to NODE.
				Builder{
					Key:        "testing.tags.ComplexMessage.workplan_str",
					KeyScope:   node,
					ValueScope: node,
					Strings:    []string{"foo"},
				}.Build(),

				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.global_str",
			msg: testingtagspb.ComplexMessage_builder{
				GlobalStr: proto.String("foo"),
			}.Build(),
			wantTags: MakeMap(
				// because it's set to value_scope=WORK_PLAN, both the key and value are
				// set to WORK_PLAN.
				Builder{
					Key:        "testing.tags.ComplexMessage.global_str",
					KeyScope:   workPlan,
					ValueScope: workPlan,
					Strings:    []string{"foo"},
				}.Build(),

				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.local_bool=true",
			msg: testingtagspb.ComplexMessage_builder{
				LocalBool: proto.Bool(true),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{true},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.local_bool__unset",
			msg:  testingtagspb.ComplexMessage_builder{}.Build(),
			wantTags: MakeMap(
				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.local_enum",
			msg: testingtagspb.ComplexMessage_builder{
				LocalEnum: testingtagspb.TestEnum_TEST_ENUM_ONE.Enum(),
			}.Build(),
			wantTags: MakeMap(
				// We pick up the numeric and string representations of the enum.
				Builder{
					Key:     "testing.tags.ComplexMessage.local_enum",
					Strings: []string{"TEST_ENUM_ONE"},
					Ints:    []int{1},
				}.Build(),

				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.rep_str",
			msg: testingtagspb.ComplexMessage_builder{
				RepStr: []string{"c", "a", "b", "a"},
			}.Build(),
			wantTags: MakeMap(
				// Sorted and unique values.
				Builder{
					Key:     "testing.tags.ComplexMessage.rep_str",
					Strings: []string{"a", "a", "b", "c"},
				}.Build(),

				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
			extraAssert: func(t *testing.T, tags Map) {
				count, _ := tags["testing.tags.ComplexMessage.rep_str"].HasValue("a")
				assert.Equal(t, uint32(2), count)
			},
		},
		{
			name: "ComplexMessage.map_sub",
			msg: testingtagspb.ComplexMessage_builder{
				MapSub: map[string]*testingtagspb.ComplexMessage_SubMessage{
					"k1": testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub1")}.Build(),
					"k2": testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub2")}.Build(),
					"k3": testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub1")}.Build(),
				},
			}.Build(),
			wantTags: MakeMap(
				// Note that the keys are ignored and the values are collapsed.
				Builder{
					Key:     "testing.tags.ComplexMessage.SubMessage.sub_tagged",
					Strings: []string{"sub1", "sub1", "sub2"},
				}.Build(),
				// This field also has an alt_key, so it's duplicated to the previous key.
				Builder{
					Key:     "previous.package.name.Message.field",
					Strings: []string{"sub1", "sub1", "sub2"},
				}.Build(),
				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.rep_sub",
			msg: testingtagspb.ComplexMessage_builder{
				RepSub: []*testingtagspb.ComplexMessage_SubMessage{
					testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub1")}.Build(),
					testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub2")}.Build(),
					testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub1")}.Build(),
				},
			}.Build(),
			wantTags: MakeMap(
				// Values are collapsed.
				Builder{
					Key:     "testing.tags.ComplexMessage.SubMessage.sub_tagged",
					Strings: []string{"sub1", "sub1", "sub2"},
				}.Build(),
				// This field also has an alt_key, so it's duplicated to the previous key.
				Builder{
					Key:     "previous.package.name.Message.field",
					Strings: []string{"sub1", "sub1", "sub2"},
				}.Build(),
				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.sub",
			msg: testingtagspb.ComplexMessage_builder{
				Sub: testingtagspb.ComplexMessage_SubMessage_builder{
					SubTagged: proto.String("hi"),
				}.Build(),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.ComplexMessage.SubMessage.sub_tagged",
					Strings: []string{"hi"},
				}.Build(),
				// This field also has an alt_key, so it's duplicated to the previous key.
				Builder{
					Key:     "previous.package.name.Message.field",
					Strings: []string{"hi"},
				}.Build(),
				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.split_index",
			msg: testingtagspb.ComplexMessage_builder{
				SplitIndex: proto.Int64(123),
			}.Build(),
			wantTags: MakeMap(
				// This has the key indexed at the WORK_PLAN level, but the value is
				// only indexed at the NODE level.
				Builder{
					Key:        "testing.tags.ComplexMessage.split_index",
					KeyScope:   workPlan,
					ValueScope: node,
					Ints:       []int{123},
				}.Build(),
				// NOTE: local_bool captures false even when unset.
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
			),
		},
		{
			name: "ComplexMessage.MULTIPLE",
			msg: testingtagspb.ComplexMessage_builder{
				LocalStr:    proto.String("foo"),
				WorkplanStr: proto.String("wp"),
				GlobalStr:   proto.String("bar"),
				// local_bool=false is picked up by default
				LocalEnum: testingtagspb.TestEnum_TEST_ENUM_ONE.Enum(),
				RepStr:    []string{"c", "a", "b", "a"},
				MapSub: map[string]*testingtagspb.ComplexMessage_SubMessage{
					"k1": testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub1")}.Build(),
					"k2": testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("sub2")}.Build(),
				},
				RepSub: []*testingtagspb.ComplexMessage_SubMessage{
					testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("rep1")}.Build(),
					testingtagspb.ComplexMessage_SubMessage_builder{SubTagged: proto.String("rep2")}.Build(),
				},
				Sub: testingtagspb.ComplexMessage_SubMessage_builder{
					SubTagged: proto.String("single"),
				}.Build(),
				SplitIndex: proto.Int64(123),
				// ExplicitPresenceBool does NOT get picked up by default.
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.ComplexMessage.local_str",
					Strings: []string{"foo"},
				}.Build(),
				Builder{
					Key:        "testing.tags.ComplexMessage.workplan_str",
					KeyScope:   node,
					ValueScope: node,
					Strings:    []string{"wp"},
				}.Build(),
				Builder{
					Key:        "testing.tags.ComplexMessage.global_str",
					KeyScope:   workPlan,
					ValueScope: workPlan,
					Strings:    []string{"bar"},
				}.Build(),
				Builder{
					Key:   "testing.tags.ComplexMessage.local_bool",
					Bools: []bool{false},
				}.Build(),
				Builder{
					Key:     "testing.tags.ComplexMessage.local_enum",
					Strings: []string{"TEST_ENUM_ONE"},
					Ints:    []int{1},
				}.Build(),
				Builder{
					Key:     "testing.tags.ComplexMessage.rep_str",
					Strings: []string{"a", "a", "b", "c"},
				}.Build(),
				Builder{
					Key:        "testing.tags.ComplexMessage.split_index",
					KeyScope:   workPlan,
					ValueScope: node,
					Ints:       []int{123},
				}.Build(),
				Builder{
					Key:     "testing.tags.ComplexMessage.SubMessage.sub_tagged",
					Strings: []string{"rep1", "rep2", "single", "sub1", "sub2"},
				}.Build(),
				Builder{
					Key:     "previous.package.name.Message.field",
					Strings: []string{"rep1", "rep2", "single", "sub1", "sub2"},
				}.Build(),
			),
		},
		{
			name: "unsupported_kind",
			msg: testingtagspb.UnsupportedKindMessage_builder{
				BadField: []byte("bad"),
			}.Build(),
			wantErr: "testing.tags.UnsupportedKindMessage.bad_field: turboci.tag: unsupported field kind bytes",
		},
		{
			name: "RecursiveMessage",
			msg: testingtagspb.RecursiveMessage_builder{
				Tagged: proto.String("root"),
				Deeper: testingtagspb.RecursiveMessage_builder{
					Tagged: proto.String("level1"),
					Deeper: testingtagspb.RecursiveMessage_builder{
						Tagged: proto.String("level2"),
					}.Build(),
				}.Build(),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.RecursiveMessage.tagged",
					Strings: []string{"level1", "level2", "root"},
				}.Build(),
			),
		},
		{
			name: "RecursiveUntaggedMessage",
			msg: testingtagspb.RecursiveUntaggedMessage_builder{
				Untagged: proto.String("root"),
				Deeper: testingtagspb.RecursiveUntaggedMessage_builder{
					Untagged: proto.String("level1"),
					Deeper: testingtagspb.RecursiveUntaggedMessage_builder{
						Untagged: proto.String("level2"),
					}.Build(),
				}.Build(),
			}.Build(),
		},
		{
			name: "MutualMessageA_with_nested_tags",
			msg: testingtagspb.MutualMessageA_builder{
				Deeper: testingtagspb.MutualMessageB_builder{
					Tagged: proto.String("b_level1"),
					Deeper: testingtagspb.MutualMessageA_builder{
						Deeper: testingtagspb.MutualMessageB_builder{
							Tagged: proto.String("b_level2"),
						}.Build(),
					}.Build(),
				}.Build(),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.MutualMessageB.tagged",
					Strings: []string{"b_level1", "b_level2"},
				}.Build(),
			),
		},
		{
			name: "MutualMessageB_with_nested_tags",
			msg: testingtagspb.MutualMessageB_builder{
				Tagged: proto.String("b_root"),
				Deeper: testingtagspb.MutualMessageA_builder{
					Deeper: testingtagspb.MutualMessageB_builder{
						Tagged: proto.String("b_nested"),
					}.Build(),
				}.Build(),
			}.Build(),
			wantTags: MakeMap(
				Builder{
					Key:     "testing.tags.MutualMessageB.tagged",
					Strings: []string{"b_nested", "b_root"},
				}.Build(),
			),
		},
		{
			name: "MutualUntaggedMessageA",
			msg: testingtagspb.MutualUntaggedMessageA_builder{
				Deeper: testingtagspb.MutualUntaggedMessageB_builder{
					Untagged: proto.String("level1"),
					Deeper: testingtagspb.MutualUntaggedMessageA_builder{
						Deeper: testingtagspb.MutualUntaggedMessageB_builder{
							Untagged: proto.String("level2"),
						}.Build(),
					}.Build(),
				}.Build(),
			}.Build(),
		},
		{
			name: "MutualUntaggedMessageB",
			msg: testingtagspb.MutualUntaggedMessageB_builder{
				Untagged: proto.String("level1"),
				Deeper: testingtagspb.MutualUntaggedMessageA_builder{
					Deeper: testingtagspb.MutualUntaggedMessageB_builder{
						Untagged: proto.String("level2"),
					}.Build(),
				}.Build(),
			}.Build(),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			// Construct a dynamicpb counterpart of `tc.msg`.
			blob, err := proto.Marshal(tc.msg)
			assert.NoErr(t, err)
			desc, err := dynreg.FindDescriptorByName(tc.msg.ProtoReflect().Descriptor().FullName())
			assert.NoErr(t, err)
			dyn := dynamicpb.NewMessage(desc.(protoreflect.MessageDescriptor))
			err = proto.Unmarshal(blob, dyn)
			assert.NoErr(t, err)

			for _, subcase := range []struct {
				name string
				msg  proto.Message
			}{
				{name: "static desc pool", msg: tc.msg},
				{name: "dynamic desc pool", msg: dyn},
			} {
				t.Run(subcase.name, func(t *testing.T) {
					tags, err := ForMessage(subcase.msg)
					if tc.wantErr != "" {
						assert.ErrLike(t, err, tc.wantErr)
					} else {
						assert.NoErr(t, err)
						assert.Match(t, tc.wantTags, tags)
						if tc.extraAssert != nil {
							tc.extraAssert(t, tags)
						}
					}
				})
			}
		})
	}
}

func TestTagsProto(t *testing.T) {
	t.Parallel()

	t.Run("basic", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:        "my.tag",
				KeyScope:   workPlan,
				ValueScope: node,
				Strings:    []string{"val1", "val1"},
				Ints:       []int{42},
			}.Build(),
		).Proto()
		assert.Len(t, protos, 1)
		assert.Match(t, orchestratorpb.Tag_builder{
			Key:   proto.String("my.tag"),
			Scope: orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN.Enum(),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					Scope:          orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue:       proto.String("val1"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(42),
				}.Build(),
			},
		}.Build(), protos[0])
	})

	t.Run("strings_sorted_lexicographically", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:        "my.tag",
				KeyScope:   workPlan,
				ValueScope: node,
				Strings: []string{
					"zebra",
					"",
					"banana",
					"apple",
					"banana",
				},
			}.Build(),
		).Proto()
		assert.Len(t, protos, 1)
		assert.Match(t, orchestratorpb.Tag_builder{
			Key:   proto.String("my.tag"),
			Scope: orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN.Enum(),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue: proto.String(""),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue: proto.String("apple"),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:          orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue:       proto.String("banana"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue: proto.String("zebra"),
				}.Build(),
			},
		}.Build(), protos[0])
	})

	t.Run("booleans_false_before_true", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:        "my.tag",
				KeyScope:   workPlan,
				ValueScope: node,
				Bools:      []bool{true, false, true},
			}.Build(),
		).Proto()
		assert.Len(t, protos, 1)
		assert.Match(t, orchestratorpb.Tag_builder{
			Key:   proto.String("my.tag"),
			Scope: orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN.Enum(),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					Scope:     orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					BoolValue: proto.Bool(false),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:          orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					BoolValue:      proto.Bool(true),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
			},
		}.Build(), protos[0])
	})

	t.Run("integers_sorted_numerically", func(t *testing.T) {
		t.Parallel()

		protos := MakeMap(
			Builder{
				Key:        "my.tag",
				KeyScope:   workPlan,
				ValueScope: node,
				Ints:       []int{42, -100, 0, 10, -100},
			}.Build(),
		).Proto()
		assert.Len(t, protos, 1)
		assert.Match(t, orchestratorpb.Tag_builder{
			Key:   proto.String("my.tag"),
			Scope: orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN.Enum(),
			Values: []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					Scope:          orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue:       proto.Int64(-100),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(0),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(10),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(42),
				}.Build(),
			},
		}.Build(), protos[0])
	})

	t.Run("mixed_type_ordering", func(t *testing.T) {
		t.Parallel()

		// StrValue < BoolValue < IntValue.
		protos := MakeMap(
			Builder{
				Key:        "my.tag",
				KeyScope:   workPlan,
				ValueScope: node,
				Ints:       []int{100, -5, 0},
				Strings:    []string{"zebra", "apple", "apple"},
				Bools:      []bool{true, false},
			}.Build(),
		).Proto()
		assert.Len(t, protos, 1)
		assert.Match(t, orchestratorpb.Tag_builder{
			Key:   proto.String("my.tag"),
			Scope: orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN.Enum(),
			Values: []*orchestratorpb.Tag_Value{
				// Strings first (lexicographical)
				orchestratorpb.Tag_Value_builder{
					Scope:          orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue:       proto.String("apple"),
					DuplicateCount: proto.Uint32(1),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					StrValue: proto.String("zebra"),
				}.Build(),
				// Booleans second (false before true)
				orchestratorpb.Tag_Value_builder{
					Scope:     orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					BoolValue: proto.Bool(false),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:     orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					BoolValue: proto.Bool(true),
				}.Build(),
				// Integers third (numerical)
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(-5),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(0),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					Scope:    orchestratorpb.ReadScope_READ_SCOPE_NODE.Enum(),
					IntValue: proto.Int64(100),
				}.Build(),
			},
		}.Build(), protos[0])
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
		assert.NoErr(t, err)
		assert.Match(t, want, tags)
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
			if assert.True(t, ok, assert.Explain("field %q was not expected", name)) {
				if !assert.Match(t, want, tag) {
					t.Logf(">> %q", name)
				}
				delete(expectedFields, name)
			}
		}
		assert.Equal(t, len(expectedFields), 0, assert.Explain("expectedFields: %v", expectedFields))
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
			KeyScope: tagpb.ReadScope_VALUE_REF.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.workplan_str": tagpb.Tag_builder{
			KeyScope:   tagpb.ReadScope_NODE.Enum(),
			ValueScope: tagpb.ReadScope_NODE.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.global_str": tagpb.Tag_builder{
			KeyScope:   tagpb.ReadScope_WORK_PLAN.Enum(),
			ValueScope: tagpb.ReadScope_WORK_PLAN.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.local_bool": tagpb.Tag_builder{
			KeyScope:   tagpb.ReadScope_VALUE_REF.Enum(),
			IndexUnset: proto.Bool(true),
		}.Build(),
		"testing.tags.ComplexMessage.local_enum": tagpb.Tag_builder{
			KeyScope: tagpb.ReadScope_VALUE_REF.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.rep_str": tagpb.Tag_builder{
			KeyScope: tagpb.ReadScope_VALUE_REF.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.split_index": tagpb.Tag_builder{
			KeyScope:   tagpb.ReadScope_WORK_PLAN.Enum(),
			ValueScope: tagpb.ReadScope_NODE.Enum(),
		}.Build(),
		"testing.tags.ComplexMessage.explicit_presence_bool": tagpb.Tag_builder{
			IndexUnset: proto.Bool(false),
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
