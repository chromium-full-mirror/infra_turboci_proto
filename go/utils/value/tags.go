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

// TagValue is an encoded orchestratorpb.Tag_Value containing only the Value
// oneof in the message (no Scope).
//
// This exists only to facilitate its use as a Go map key within the current
// process.
type TagValue struct{ encodedTagValue string }

func makeTagValue(tv *orchestratorpb.Tag_Value) (TagValue, orchestratorpb.ReadScope, bool) {
	if !tv.HasData() {
		return TagValue{}, 0, false
	}
	scope := tv.GetScope()
	if tv.HasScope() {
		tv = proto.CloneOf(tv)
		tv.ClearScope()
	}
	enc, err := proto.MarshalOptions{Deterministic: true}.Marshal(tv)
	if err != nil {
		return TagValue{}, 0, false
	}
	return TagValue{string(enc)}, scope, true
}

// Proto unmarshals the encoded Tag_Value.
func (v TagValue) Proto() *orchestratorpb.Tag_Value {
	ret := orchestratorpb.Tag_Value{}
	if err := proto.Unmarshal([]byte(v.encodedTagValue), &ret); err != nil {
		panic(fmt.Errorf("value.TagValue.Proto(): %s", err))
	}
	return &ret
}

func (v TagValue) String() string {
	return v.Proto().String()
}

type ScopeCount struct {
	Scope orchestratorpb.ReadScope
	// Total count (not duplicate count)
	Count uint32
}

func (s *ScopeCount) Increment(scope orchestratorpb.ReadScope) {
	s.Scope = max(s.Scope, scope)
	s.Count++
}

// Tag is an easier in-process representation of an orchestratorpb.Tag.
type Tag struct {
	Scope  orchestratorpb.ReadScope
	Values map[TagValue]*ScopeCount
}

func (t *Tag) getScopeCount(tv TagValue) *ScopeCount {
	if t.Values == nil {
		t.Values = map[TagValue]*ScopeCount{}
	}
	cur := t.Values[tv]
	if cur == nil {
		cur = &ScopeCount{}
		t.Values[tv] = cur
	}
	return cur
}

func (t *Tag) AddValue(tv *orchestratorpb.Tag_Value) {
	enc, scope, ok := makeTagValue(tv)
	if !ok {
		return
	}
	t.getScopeCount(enc).Increment(scope)
}

// Proto returns this as an orchestratorpb.Tag with the given key.
func (t *Tag) Proto(key string) *orchestratorpb.Tag {
	values := make([]*orchestratorpb.Tag_Value, 0, len(t.Values))
	for vt, scopeCount := range t.Values {
		vtp := vt.Proto()
		vtp.SetScope(scopeCount.Scope)
		if scopeCount.Count > 1 {
			vtp.SetDuplicateCount(scopeCount.Count - 1)
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
	return orchestratorpb.Tag_builder{
		Key:    &key,
		Scope:  t.Scope.Enum(),
		Values: values,
	}.Build()
}

// Tags is a convenient form of, and convertible to, a repeated set of Tags
// protos.
type Tags map[string]*Tag

// Proto converts this Tags into a list of orchestratorpb.Tag protos.
func (t Tags) Proto() []*orchestratorpb.Tag {
	ret := make([]*orchestratorpb.Tag, 0, len(t))
	for k, val := range t {
		ret = append(ret, val.Proto(k))
	}
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

// Add adds tag data in proto form.
func (t Tags) Add(tags iter.Seq[*orchestratorpb.Tag]) {
	for tag := range tags {
		dat := t.getData(tag.GetKey())
		dat.Scope = max(dat.Scope, tag.GetScope())
		for _, value := range tag.GetValues() {
			dat.AddValue(value)
		}
	}
}
