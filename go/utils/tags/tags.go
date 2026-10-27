// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package tags

import (
	"cmp"
	"fmt"
	"iter"
	"slices"
	"strings"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	tagpb "go.chromium.org/turboci/proto/go/tag"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
)

// ForMessage extracts all TurboCI tags/data for the given message.
//
// Usually this is called automatically via [Write].
func ForMessage(msg proto.Message) (Map, error) {
	if msg == nil {
		return nil, nil
	}
	ret := Map{}
	msgR := msg.ProtoReflect()
	extractor, err := getTagExtractor(msgR.Descriptor())
	if err != nil {
		return nil, err
	}
	extractor.extract(ret, msgR)
	if len(ret) == 0 {
		ret = nil
	}
	return ret, nil
}

// FieldTags is an `iter.Seq2[protoreflect.FieldDescriptor, *tagpb.Tag]` which
// yields field + normalized Tag protos for the type `M`.
//
// This allows you to answer "If I used ForMessage on an instance of M, what
// tags could it contain?"
//
// Note: You can turn this into a map with [maps.Collect].
func FieldTags[M proto.Message](yield func(protoreflect.FieldDescriptor, *tagpb.Tag) bool) {
	var m M
	msg := m.ProtoReflect().Descriptor()
	te, err := getTagExtractor(msg)
	if err != nil {
		return
	}
	visited := map[protoreflect.MessageDescriptor]struct{}{}

	var walk func(desc protoreflect.MessageDescriptor, te tagExtractor) iter.Seq2[protoreflect.FieldDescriptor, *tagpb.Tag]
	walk = func(desc protoreflect.MessageDescriptor, te tagExtractor) iter.Seq2[protoreflect.FieldDescriptor, *tagpb.Tag] {
		return func(yield func(protoreflect.FieldDescriptor, *tagpb.Tag) bool) {
			if _, ok := visited[desc]; ok {
				return
			}
			visited[desc] = struct{}{}

			for field, tfe := range te {
				if tfe.extractScalar != nil {
					tag := proto.GetExtension(field.Options(), tagpb.E_Tag).(*tagpb.Tag)
					if tag != nil {
						if !yield(field, normalizeTag(tag, field.Kind())) {
							return
						}
					}
				} else {
					for field, tag := range walk(submsgDesc(field), tfe.recurseMessage) {
						if !yield(field, tag) {
							return
						}
					}
				}
			}
		}
	}
	walk(m.ProtoReflect().Descriptor(), te)(yield)
}

// tagValue is an encoded orchestratorpb.Tag_Value containing only the Value
// oneof in the message.
//
// This exists only to facilitate its use as a Go map key within the current
// process.
type tagValue struct{ encodedTagValue string }

// makeTagValue makes a `tagValue` from a Tag_Value proto.
//
// Returns the encoded value plus OK (which can only be false if `tv` does not
// have the `data` oneof set to anything).
func makeTagValue(tv *orchestratorpb.Tag_Value) (tagValue, bool) {
	if !tv.HasData() {
		return tagValue{}, false
	}
	if tv.HasIndexed() || tv.HasDuplicateCount() {
		tv = proto.CloneOf(tv)
		tv.ClearIndexed()
		tv.ClearDuplicateCount()
	}
	enc, err := proto.MarshalOptions{Deterministic: true}.Marshal(tv)
	if err != nil {
		panic(fmt.Errorf("value.makeTagValue: %s", err))
	}
	return tagValue{string(enc)}, true
}

// proto unmarshals the encoded Tag_Value.
func (v tagValue) proto() *orchestratorpb.Tag_Value {
	ret := orchestratorpb.Tag_Value{}
	if err := proto.Unmarshal([]byte(v.encodedTagValue), &ret); err != nil {
		panic(fmt.Errorf("value.TagValue.Proto(): %s", err))
	}
	return &ret
}

func (v tagValue) String() string {
	return v.proto().String()
}

// perValueState tracker per-value state when constructing a tag.
type perValueState struct {
	// indexed is true if this value was indexed at least once.
	indexed bool
	// Total count of instances of this particular value (not duplicate count).
	count uint32
}

// updates updates the perValueState based on the given delta.
func (s *perValueState) update(indexed bool, delta uint32) {
	s.indexed = s.indexed || indexed
	s.count += delta
}

// Tag is an easier in-process representation of an orchestratorpb.Tag.
//
// Primarily intended to be used in conjunction with [ForMessage], rarely
// constructed directly (perhaps only in tests).
type Tag struct {
	indexed bool
	values  map[tagValue]*perValueState
}

// Indexed is true if any data in this tag is indexed.
func (t *Tag) Indexed() bool {
	return t.indexed
}

// Values returns all Values contained in this Tag, in normalized order.
func (t *Tag) Values() []*orchestratorpb.Tag_Value {
	values := make([]*orchestratorpb.Tag_Value, 0, len(t.values))

	for vt, state := range t.values {
		vtp := vt.proto()
		if state.indexed {
			vtp.SetIndexed(state.indexed)
		}
		if state.count > 1 {
			vtp.SetDuplicateCount(state.count - 1)
		}
		values = append(values, vtp)
	}

	// Sort all the values.
	slices.SortFunc(values, func(a, b *orchestratorpb.Tag_Value) int {
		if typeOrder := a.WhichData() - b.WhichData(); typeOrder != 0 {
			return int(typeOrder)
		}
		switch a.WhichData() {
		case orchestratorpb.Tag_Value_IntValue_case:
			return cmp.Compare(a.GetIntValue(), b.GetIntValue())
		case orchestratorpb.Tag_Value_BoolValue_case:
			// Unfortunately cmp.Compare does not work here:
			// https://github.com/golang/go/issues/61643
			abool, bbool := a.GetBoolValue(), b.GetBoolValue()
			if abool == bbool {
				return 0
			}
			if !abool {
				return -1
			}
			return 1
		case orchestratorpb.Tag_Value_StrValue_case:
			return strings.Compare(a.GetStrValue(), b.GetStrValue())
		default:
			panic("impossible")
		}
	})

	return values
}

// HasValue checks to see if this Tag contains the given value.
//
// value must be one of the following types:
//   - *orchestratorpb.Tag_Value (`indexed` and `duplicate_count` are ignored)
//   - int, int32, int64, uint32
//   - string
//   - bool
//
// Returns the *total* count of this value (not duplicate count), plus if it
// was indexed or not.
//
// If the value is an invalid type or does not exist in this tag, count is zero.
func (t *Tag) HasValue(value any) (count uint32, indexed bool) {
	enc, ok := makeTagValue(newTagValue(value, false))
	if !ok {
		return 0, false
	}
	got, ok := t.values[enc]
	if !ok {
		return 0, false
	}
	return got.count, got.indexed
}

// perValue returns the per-value state associated with the value.
func (t *Tag) perValue(tv tagValue) *perValueState {
	if t.values == nil {
		t.values = map[tagValue]*perValueState{}
	}
	cur := t.values[tv]
	if cur == nil {
		cur = &perValueState{}
		t.values[tv] = cur
	}
	return cur
}

// AddValue inserts a value of the tag.
//
// If the value is indexed, the tag is marked as being indexed as well.
func (t *Tag) AddValue(tv *orchestratorpb.Tag_Value) {
	t.indexed = t.indexed || tv.GetIndexed()
	if enc, ok := makeTagValue(tv); ok {
		t.perValue(enc).update(tv.GetIndexed(), tv.GetDuplicateCount()+1)
	}
}

// Proto returns this as an orchestratorpb.Tag with the given key.
func (t *Tag) Proto(key string) *orchestratorpb.Tag {
	var indexed *bool
	if t.indexed {
		indexed = &t.indexed
	}
	return orchestratorpb.Tag_builder{
		Key:     &key,
		Indexed: indexed,
		Values:  t.Values(),
	}.Build()
}

// Map is a convenient form of, and convertible to, a repeated set of Tag
// protos.
type Map map[string]*Tag

// MakeMap is a helper function for:
//
//	t := Tags{}
//	t.Add(slices.Values(tags))
//	return t
func MakeMap(tags ...*orchestratorpb.Tag) Map {
	t := Map{}
	t.Add(slices.Values(tags))
	return t
}

// Proto converts this Tags into a normalized list of orchestratorpb.Tag protos.
func (t Map) Proto() []*orchestratorpb.Tag {
	ret := make([]*orchestratorpb.Tag, 0, len(t))
	for k, val := range t {
		ret = append(ret, val.Proto(k))
	}
	slices.SortFunc(ret, func(a, b *orchestratorpb.Tag) int {
		return cmp.Compare(a.GetKey(), b.GetKey())
	})
	return ret
}

// tagByKey constructs *Tag if necessary or returns the existing one.
func (t Map) tagByKey(key string) *Tag {
	cur := t[key]
	if cur == nil {
		cur = &Tag{}
		t[key] = cur
	}
	return cur
}

// Add adds tag data in proto form from an iter, merging tags with
// identical keys.
func (t Map) Add(tags iter.Seq[*orchestratorpb.Tag]) {
	for tag := range tags {
		dat := t.tagByKey(tag.GetKey())
		dat.indexed = dat.indexed || tag.GetIndexed()
		for _, value := range tag.GetValues() {
			dat.AddValue(value)
		}
	}
}

// newTagValue makes a new Tag_Value.
func newTagValue(v any, indexed bool) *orchestratorpb.Tag_Value {
	tv := &orchestratorpb.Tag_Value{}
	if indexed {
		tv.SetIndexed(indexed)
	}
	switch v := any(v).(type) {
	case *orchestratorpb.Tag_Value:
		return v
	case string:
		tv.SetStrValue(v)
	case bool:
		tv.SetBoolValue(v)
	case int:
		tv.SetIntValue(int64(v))
	case int32:
		tv.SetIntValue(int64(v))
	case int64:
		tv.SetIntValue(int64(v))
	case uint32:
		tv.SetIntValue(int64(v))
	default:
		panic(fmt.Errorf("unsupported TagValue type: %T", v))
	}
	return tv
}

// Builder allows easier construction of a Tag.
type Builder struct {
	// Key is the tag to construct.
	Key string

	// Indexed is true to indicate the tag must be indexed.
	Indexed bool
	// IndexKeyOnly indicates to index only tag's key, but not its values.
	IndexKeyOnly bool

	// Strings are all string values of the tag, if any.
	Strings []string
	// Bools are all bool values of the tag, if any.
	Bools []bool
	// Ints are all integer values of the tag, if any.
	Ints []int
}

// Build renders the TagTemplate to a Tag.
func (t Builder) Build() *orchestratorpb.Tag {
	tg := Tag{indexed: t.Indexed || t.IndexKeyOnly}
	indexValues := t.Indexed && !t.IndexKeyOnly
	for _, val := range t.Strings {
		tg.AddValue(newTagValue(val, indexValues))
	}
	for _, val := range t.Bools {
		tg.AddValue(newTagValue(val, indexValues))
	}
	for _, val := range t.Ints {
		tg.AddValue(newTagValue(val, indexValues))
	}
	return tg.Proto(t.Key)
}
