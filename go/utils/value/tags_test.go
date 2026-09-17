// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/emptypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	testingtagspb "go.chromium.org/turboci/proto/go/testing/tags"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

const (
	valueRef = orchestratorpb.ReadScope_READ_SCOPE_VALUE_REF
	node     = orchestratorpb.ReadScope_READ_SCOPE_NODE
	workPlan = orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN
)

type taggableValue interface {
	~string | ~bool | ~int | ~int32 | ~int64 | ~uint32 | TagValue
}

func tagVal[T taggableValue](v T) TagValue {
	var tv *orchestratorpb.Tag_Value
	switch v := any(v).(type) {
	case TagValue:
		return v
	case string:
		tv = orchestratorpb.Tag_Value_builder{StrValue: proto.String(v)}.Build()
	case bool:
		tv = orchestratorpb.Tag_Value_builder{BoolValue: proto.Bool(v)}.Build()
	case int:
		tv = orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(int64(v))}.Build()
	case int64:
		tv = orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(v)}.Build()
	case int32:
		tv = orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(int64(v))}.Build()
	case uint32:
		tv = orchestratorpb.Tag_Value_builder{IntValue: proto.Int64(int64(v))}.Build()
	default:
		panic(fmt.Errorf("unsupported tagVal type: %T", v))
	}
	enc, _, ok := makeTagValue(tv)
	if !ok {
		panic(fmt.Errorf("failed to make TagValue from %v", v))
	}
	return enc
}

func tag[T taggableValue](vals ...T) *Tag {
	return scopedTag(valueRef, valueRef, vals...)
}

func scopedTag[T taggableValue](keyScope, valScope orchestratorpb.ReadScope, vals ...T) *Tag {
	t := &Tag{
		Scope:  keyScope,
		Values: make(map[TagValue]*ScopeCount, len(vals)),
	}
	for _, v := range vals {
		t.getScopeCount(tagVal(v)).increment(valScope, 1)
	}
	return t
}

func TestTagsFor(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name     string
		msg      proto.Message
		wantErr  string
		wantTags Tags
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
			wantTags: Tags{
				"testing.tags.MyMessage.tagged_field": tag("hello"),
			},
		},
		{
			name: "ComplexMessage.local_str",
			msg: testingtagspb.ComplexMessage_builder{
				LocalStr: proto.String("foo"),
			}.Build(),
			wantTags: Tags{
				"testing.tags.ComplexMessage.local_str": tag("foo"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.workplan_str",
			msg: testingtagspb.ComplexMessage_builder{
				WorkplanStr: proto.String("foo"),
			}.Build(),
			wantTags: Tags{
				// because it's set to value_scope=NODE, both the key and value are
				// set to NODE.
				"testing.tags.ComplexMessage.workplan_str": scopedTag(node, node, "foo"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.global_str",
			msg: testingtagspb.ComplexMessage_builder{
				GlobalStr: proto.String("foo"),
			}.Build(),
			wantTags: Tags{
				// because it's set to value_scope=WORK_PLAN, both the key and value are
				// set to WORK_PLAN.
				"testing.tags.ComplexMessage.global_str": scopedTag(workPlan, workPlan, "foo"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.local_bool=true",
			msg: testingtagspb.ComplexMessage_builder{
				LocalBool: proto.Bool(true),
			}.Build(),
			wantTags: Tags{
				"testing.tags.ComplexMessage.local_bool": tag(true),
			},
		},
		{
			name: "ComplexMessage.local_bool__unset",
			msg:  testingtagspb.ComplexMessage_builder{}.Build(),
			wantTags: Tags{
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.local_enum",
			msg: testingtagspb.ComplexMessage_builder{
				LocalEnum: testingtagspb.TestEnum_TEST_ENUM_ONE.Enum(),
			}.Build(),
			wantTags: Tags{
				// We pick up the numeric and string representations of the enum.
				"testing.tags.ComplexMessage.local_enum": tag(tagVal(1), tagVal("TEST_ENUM_ONE")),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.rep_str",
			msg: testingtagspb.ComplexMessage_builder{
				RepStr: []string{"c", "a", "b", "a"},
			}.Build(),
			wantTags: Tags{
				// Sorted and unique values.
				"testing.tags.ComplexMessage.rep_str": tag("a", "a", "b", "c"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
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
			wantTags: Tags{
				// Note that the keys are ignored and the values are collapsed.
				"testing.tags.ComplexMessage.SubMessage.sub_tagged": tag("sub1", "sub1", "sub2"),
				// This field also has an alt_key, so it's duplicated to the previous key.
				"previous.package.name.Message.field": tag("sub1", "sub1", "sub2"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
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
			wantTags: Tags{
				// Values are collapsed.
				"testing.tags.ComplexMessage.SubMessage.sub_tagged": tag("sub1", "sub1", "sub2"),
				// This field also has an alt_key, so it's duplicated to the previous key.
				"previous.package.name.Message.field": tag("sub1", "sub1", "sub2"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.sub",
			msg: testingtagspb.ComplexMessage_builder{
				Sub: testingtagspb.ComplexMessage_SubMessage_builder{
					SubTagged: proto.String("hi"),
				}.Build(),
			}.Build(),
			wantTags: Tags{
				"testing.tags.ComplexMessage.SubMessage.sub_tagged": tag("hi"),
				// This field also has an alt_key, so it's duplicated to the previous key.
				"previous.package.name.Message.field": tag("hi"),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
		},
		{
			name: "ComplexMessage.split_index",
			msg: testingtagspb.ComplexMessage_builder{
				SplitIndex: proto.Int64(123),
			}.Build(),
			wantTags: Tags{
				// This has the key indexed at the WORK_PLAN level, but the value is
				// only indexed at the NODE level.
				"testing.tags.ComplexMessage.split_index": scopedTag(workPlan, node, 123),
				// NOTE: local_bool captures false even when unset.
				"testing.tags.ComplexMessage.local_bool": tag(false),
			},
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
			wantTags: Tags{
				"testing.tags.ComplexMessage.local_str":             tag("foo"),
				"testing.tags.ComplexMessage.workplan_str":          scopedTag(node, node, "wp"),
				"testing.tags.ComplexMessage.global_str":            scopedTag(workPlan, workPlan, "bar"),
				"testing.tags.ComplexMessage.local_bool":            tag(false),
				"testing.tags.ComplexMessage.local_enum":            tag(tagVal(1), tagVal("TEST_ENUM_ONE")),
				"testing.tags.ComplexMessage.rep_str":               tag("a", "a", "b", "c"),
				"testing.tags.ComplexMessage.split_index":           scopedTag(workPlan, node, 123),
				"testing.tags.ComplexMessage.SubMessage.sub_tagged": tag("rep1", "rep2", "single", "sub1", "sub2"),
				"previous.package.name.Message.field":               tag("rep1", "rep2", "single", "sub1", "sub2"),
			},
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
			wantTags: Tags{
				"testing.tags.RecursiveMessage.tagged": tag("level1", "level2", "root"),
			},
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
			wantTags: Tags{
				"testing.tags.MutualMessageB.tagged": tag("b_level1", "b_level2"),
			},
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
			wantTags: Tags{
				"testing.tags.MutualMessageB.tagged": tag("b_nested", "b_root"),
			},
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

			tags, err := TagsFor(tc.msg)
			if tc.wantErr != "" {
				assert.ErrLike(t, err, tc.wantErr)
			} else {
				assert.NoErr(t, err)
				assert.Match(t, tc.wantTags, tags)
			}
		})
	}
}

func TestTagsProto(t *testing.T) {
	t.Parallel()

	t.Run("basic", func(t *testing.T) {
		t.Parallel()

		tags := Tags{
			"my.tag": scopedTag(workPlan, node, tagVal("val1"), tagVal(42), tagVal("val1")),
		}
		protos := tags.Proto()
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

		tags := Tags{
			"my.tag": scopedTag(workPlan, node, "zebra", "", "banana", "apple", "banana"),
		}
		protos := tags.Proto()
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

		tags := Tags{
			"my.tag": scopedTag(workPlan, node, true, false, true),
		}
		protos := tags.Proto()
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

		tags := Tags{
			"my.tag": scopedTag(workPlan, node, 42, -100, 0, 10, -100),
		}
		protos := tags.Proto()
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

		// StrValue (case 3) < BoolValue (case 4) < IntValue (case 5).
		// Input values are provided in scrambled order across types.
		tags := Tags{
			"my.tag": scopedTag(workPlan, node,
				tagVal(100),
				tagVal("zebra"),
				tagVal(true),
				tagVal(-5),
				tagVal("apple"),
				tagVal(false),
				tagVal("apple"),
				tagVal(0),
			),
		}
		protos := tags.Proto()
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

	want := Tags{
		"testing.tags.LoopMessageD.tagged": tag("d_nested", "d_root"),
	}

	for range 10 {
		tagExtractorPoolMu.Lock()
		clear(tagExtractorPool)
		tagExtractorPoolMu.Unlock()

		tags, err := TagsFor(msg)
		assert.NoErr(t, err)
		assert.Match(t, want, tags)
	}
}
