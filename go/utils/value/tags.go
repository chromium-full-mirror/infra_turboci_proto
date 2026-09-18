// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"cmp"
	"fmt"
	"iter"
	"slices"
	"strings"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"google.golang.org/protobuf/proto"
)

// TagsFor extracts all TurboCI tags/data for the given message.
//
// Usually this is called automatically via [Write].
func TagsFor(msg proto.Message) (Tags, error) {
	if msg == nil {
		return nil, nil
	}
	ret := Tags{}
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

// tagValue is an encoded orchestratorpb.Tag_Value containing only the Value
// oneof in the message (no Scope).
//
// This exists only to facilitate its use as a Go map key within the current
// process.
type tagValue struct{ encodedTagValue string }

func makeTagValue(value any) (tagValue, bool) {
	tv := &orchestratorpb.Tag_Value{}
	switch v := value.(type) {
	case *orchestratorpb.Tag_Value:
		tv = v
		if !tv.HasData() {
			return tagValue{}, false
		}
		if tv.HasScope() || tv.HasDuplicateCount() {
			tv = proto.CloneOf(tv)
			tv.ClearScope()
			tv.ClearDuplicateCount()
		}
	case string:
		tv.SetStrValue(v)
	case bool:
		tv.SetBoolValue(v)
	case int:
		tv.SetIntValue(int64(v))
	case int64:
		tv.SetIntValue(int64(v))
	case int32:
		tv.SetIntValue(int64(v))
	case uint32:
		tv.SetIntValue(int64(v))
	default:
		return tagValue{}, false
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

// scopeCount aggregates the maximum observed read scope of a particular tag
// value and the total number of instances of this value.
type scopeCount struct {
	// scope indicates the level at which this *value* can be read.
	scope orchestratorpb.ReadScope
	// Total count of instances of this particular value (not duplicate count).
	count uint32
}

// increment sets Scope to the max of the current and given scopes, and
// increments count by `delta`.
func (s *scopeCount) increment(scope orchestratorpb.ReadScope, delta uint32) {
	s.scope = max(s.scope, scope)
	s.count += delta
}

// Tag is an easier in-process representation of an orchestratorpb.Tag.
//
// Primarily intended to be used in conjunction with [TagsFor], rarely
// constructed directly (perhaps only in tests).
type Tag struct {
	// Scope indicates the level at which the tag *key* can be read.
	Scope orchestratorpb.ReadScope

	values map[tagValue]*scopeCount
}

// Values returns all Values contained in this Tag, in normalized order.
func (t *Tag) Values() []*orchestratorpb.Tag_Value {
	values := make([]*orchestratorpb.Tag_Value, 0, len(t.values))

	for vt, scopeCount := range t.values {
		vtp := vt.proto()
		vtp.SetScope(scopeCount.scope)
		if scopeCount.count > 1 {
			vtp.SetDuplicateCount(scopeCount.count - 1)
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
//   - *orchestratorpb.Tag_Value (scope and duplicate count are ignored)
//   - int, int32, int64, uint32
//   - string
//   - bool
//
// Returns the *total* count of this value (not duplicate count), plus the
// scope.
//
// If the value is an invalid type or does not exist in this tag, count is zero.
func (t *Tag) HasValue(value any) (count uint32, scope orchestratorpb.ReadScope) {
	enc, ok := makeTagValue(value)
	if !ok {
		return 0, 0
	}
	got, ok := t.values[enc]
	if !ok {
		return 0, 0
	}
	return got.count, got.scope
}

// NewTag constructs a Tag given enumeration of its values.
func NewTag(tv ...*orchestratorpb.Tag_Value) *Tag {
	t := &Tag{values: make(map[tagValue]*scopeCount, len(tv))}
	for _, v := range tv {
		t.AddValue(v)
	}
	return t
}

func (t *Tag) getScopeCount(tv tagValue) *scopeCount {
	if t.values == nil {
		t.values = map[tagValue]*scopeCount{}
	}
	cur := t.values[tv]
	if cur == nil {
		cur = &scopeCount{}
		t.values[tv] = cur
	}
	return cur
}

// AddValue inserts a value of the tag.
func (t *Tag) AddValue(tv *orchestratorpb.Tag_Value) {
	enc, ok := makeTagValue(tv)
	if !ok {
		return
	}
	t.getScopeCount(enc).increment(tv.GetScope(), tv.GetDuplicateCount()+1)
}

// Proto returns this as an orchestratorpb.Tag with the given key.
func (t *Tag) Proto(key string) *orchestratorpb.Tag {
	return orchestratorpb.Tag_builder{
		Key:    &key,
		Scope:  t.Scope.Enum(),
		Values: t.Values(),
	}.Build()
}

// Tags is a convenient form of, and convertible to, a repeated set of Tags
// protos.
type Tags map[string]*Tag

// Proto converts this Tags into a normalized list of orchestratorpb.Tag protos.
func (t Tags) Proto() []*orchestratorpb.Tag {
	ret := make([]*orchestratorpb.Tag, 0, len(t))
	for k, val := range t {
		ret = append(ret, val.Proto(k))
	}
	slices.SortFunc(ret, func(a, b *orchestratorpb.Tag) int {
		return cmp.Compare(a.GetKey(), b.GetKey())
	})
	return ret
}

func (t Tags) getData(key string) *Tag {
	cur := t[key]
	if cur == nil {
		cur = &Tag{}
		t[key] = cur
	}
	return cur
}

// Add adds tag data in proto form, merging tags with identical keys.
func (t Tags) Add(tags iter.Seq[*orchestratorpb.Tag]) {
	for tag := range tags {
		dat := t.getData(tag.GetKey())
		dat.Scope = max(dat.Scope, tag.GetScope())
		for _, value := range tag.GetValues() {
			dat.AddValue(value)
		}
	}
}
