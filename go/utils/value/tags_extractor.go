// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"iter"
	"sync"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	tagspb "go.chromium.org/turboci/proto/go/tags"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoreflect"
)

// tagFieldExtractor understands how to extract tag(s) for one specific field
// in one specific proto message.
type tagFieldExtractor struct {
	// captureUnset, if true, will cause tag extraction for this field to occur
	// even if `msg.Has(field)` would return false.
	//
	// This defaults to `true` for bool fields, and false for all other field
	// types.
	captureUnset bool

	// toTags yields all tags for this field.
	// it is `nil` if this field does not have extractable values.
	toTags func(v protoreflect.Value) iter.Seq[*orchestratorpb.Tag]

	// otherwise, recurseMessage will be set with zero or more of [isList, isMap].
	recurseMessage tagExtractor
	isList         bool
	isMap          bool
}

// extract updates `tags` for this field, given the value `val`.
func (t *tagFieldExtractor) extract(tags Tags, val protoreflect.Value) {
	// `toTags` != nil means that we need to directly extract from `val`.
	if t.toTags != nil {
		tags.Add(t.toTags(val))
		return
	}

	// Otherwise, we need to recurse; this is either singleton recursion, list
	// recursion, or map (values) recursion.
	it := func(yield func(protoreflect.Message) bool) {
		yield(val.Message())
	}
	if t.isMap {
		it = func(yield func(protoreflect.Message) bool) {
			for _, val := range val.Map().Range {
				if !yield(val.Message()) {
					return
				}
			}
		}
	} else if t.isList {
		it = func(yield func(protoreflect.Message) bool) {
			for val := range rangeProtoSeq(val.List()) {
				if !yield(val.Message()) {
					return
				}
			}
		}
	}

	for msg := range it {
		t.recurseMessage.extract(tags, msg)
	}
}

// tagExtractor knows how to extract ValueTags from some specific message type.
//
// The keys of the map are the fields which may need some kind of extraction.
type tagExtractor map[protoreflect.FieldDescriptor]*tagFieldExtractor

// extract walks the extractor, updating `tags` for any relevant fields in
// `msg`.
func (t tagExtractor) extract(tags Tags, msg protoreflect.Message) {
	for field, extractor := range t {
		if extractor.captureUnset || msg.Has(field) {
			extractor.extract(tags, msg.Get(field))
		}
	}
}

// tagExtractorPoolEntry is a simple union of either a tagExtractor or an
// error, used as the value of [tagExtractorPool] to cache the extractor or err
// on a per-message-type basis.
//
// At most one of `extractor` or `err` will be set. If both are unset it means
// that the message has no extractable fields.
type tagExtractorPoolEntry struct {
	extractor tagExtractor
	err       error
}

var (
	// tagExtractorPoolMu synchronizes access to [tagExtractorPool].
	tagExtractorPoolMu sync.RWMutex

	// a nil *tagExtractor and nil error indicates that this message doesn't
	// transitively have any tagged fields.
	tagExtractorPool = map[protoreflect.MessageDescriptor]tagExtractorPoolEntry{}
)

// rangeProtoSeq converts a Len()+Get(int) E object into an iter.Seq[E].
func rangeProtoSeq[S interface {
	Len() int
	Get(int) E
}, E any](seq S) iter.Seq[E] {
	return func(yield func(E) bool) {
		for i := 0; i < seq.Len(); i++ {
			if !yield(seq.Get(i)) {
				return
			}
		}
	}
}

// makeFieldExtractor returns a function which extracts a *single* scalar value
// into one *or more* Tag_Value proto messages.
//
// Returns nil if extraction from this field kind is not possible.
func makeFieldExtractor(field protoreflect.FieldDescriptor) func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
	switch field.Kind() {
	case protoreflect.EnumKind:
		vals := field.Enum().Values()

		return func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
			enum := v.Enum()
			return []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(int64(enum)),
				}.Build(),
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String(string(vals.ByNumber(enum).Name())),
				}.Build(),
			}
		}

	case protoreflect.BoolKind:
		return func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
			return []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					BoolValue: proto.Bool(v.Bool()),
				}.Build(),
			}
		}

	case protoreflect.StringKind:
		return func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
			return []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					StrValue: proto.String(v.String()),
				}.Build(),
			}
		}

	case protoreflect.Int32Kind, protoreflect.Int64Kind,
		protoreflect.Sint32Kind, protoreflect.Sint64Kind,
		protoreflect.Sfixed32Kind, protoreflect.Sfixed64Kind:

		return func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
			return []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(v.Int()),
				}.Build(),
			}
		}

	case protoreflect.Fixed32Kind, protoreflect.Uint32Kind:
		return func(v protoreflect.Value) []*orchestratorpb.Tag_Value {
			return []*orchestratorpb.Tag_Value{
				orchestratorpb.Tag_Value_builder{
					IntValue: proto.Int64(int64(v.Uint())),
				}.Build(),
			}
		}
	}

	return nil
}

// calculateScopes calculates the effective captureUnset, keyScope and valueScope
// for a field, given the tag annotation proto and the kind of the field.
//
// In particular, this converts the source-annotation friendly tagspb.ReadScope
// to the API orchestratorpb.ReadScope enum, ensures that keyScope is >=
// valueScope, and applies the default index_unset logic for bool fields.
func calculateScopes(tag *tagspb.Tag, kind protoreflect.Kind) (captureUnset bool, keyScope, valueScope orchestratorpb.ReadScope) {
	toReadScope := func(in tagspb.ReadScope) orchestratorpb.ReadScope {
		switch in {
		case tagspb.ReadScope_NODE:
			return orchestratorpb.ReadScope_READ_SCOPE_NODE
		case tagspb.ReadScope_WORK_PLAN:
			return orchestratorpb.ReadScope_READ_SCOPE_WORK_PLAN
		}
		return orchestratorpb.ReadScope_READ_SCOPE_VALUE_REF
	}

	valueScope = toReadScope(tag.GetValueScope())
	keyScope = max(valueScope, toReadScope(tag.GetKeyScope()))

	if tag.HasIndexUnset() {
		captureUnset = tag.GetIndexUnset()
	} else {
		// Bool defaults to capturing unset.
		captureUnset = kind == protoreflect.BoolKind
	}

	return
}

// makeTagFieldExtractor returns a tagFieldExtractor for the field + tag,
// or an error if this field cannot be tagged.
func makeTagFieldExtractor(field protoreflect.FieldDescriptor, tag *tagspb.Tag) (*tagFieldExtractor, error) {
	keys := append([]string{string(field.FullName())}, tag.GetAltKey()...)
	codec := makeFieldExtractor(field)
	if codec == nil {
		return nil, fmt.Errorf("%s: turboci.tag: unsupported field kind %s", field.FullName(), field.Kind())
	}
	if field.IsMap() {
		return nil, fmt.Errorf("%s: turboci.tag: unsupported field: map", field.FullName())
	}

	captureUnset, keyScope, valueScope := calculateScopes(tag, field.Kind())
	if field.IsList() {
		return &tagFieldExtractor{
			captureUnset: captureUnset,
			toTags: func(v protoreflect.Value) iter.Seq[*orchestratorpb.Tag] {
				lst := v.List()

				return func(yield func(*orchestratorpb.Tag) bool) {
					for i := 0; i < lst.Len(); i++ {
						values := codec(lst.Get(i))
						for _, val := range values {
							val.SetScope(valueScope)
						}
						for _, key := range keys {
							tag := orchestratorpb.Tag_builder{
								Key:    &key,
								Scope:  &keyScope,
								Values: values,
							}.Build()
							if !yield(tag) {
								return
							}
						}
					}
				}
			},
		}, nil
	}

	return &tagFieldExtractor{
		captureUnset: captureUnset,
		toTags: func(v protoreflect.Value) iter.Seq[*orchestratorpb.Tag] {
			values := codec(v)
			for _, val := range values {
				val.SetScope(valueScope)
			}
			return func(yield func(*orchestratorpb.Tag) bool) {
				for _, key := range keys {
					tag := orchestratorpb.Tag_builder{
						Key:    &key,
						Scope:  &keyScope,
						Values: values,
					}.Build()
					if !yield(tag) {
						return
					}
				}
			}
		},
	}, nil
}

// computeTagExtractorLocked computes, caches and returns the tagExtractor for
// messages whose type is `msg`.
func computeTagExtractorLocked(msg protoreflect.MessageDescriptor) (tagExtractor, error) {
	entry, has := tagExtractorPool[msg]
	if has {
		return entry.extractor, entry.err
	}

	// Ok, we need to generate a new extractor for this message descriptor.
	extractor := tagExtractor{}
	entry = tagExtractorPoolEntry{extractor: extractor}
	// Set it while we recurse.
	tagExtractorPool[msg] = entry

	fields := msg.Fields()
	var msgFields []protoreflect.FieldDescriptor

	// Loop over all fields - if they are tagged, add them to extractor.
	for field := range rangeProtoSeq(fields) {
		tag := proto.GetExtension(field.Options(), tagspb.E_Tag).(*tagspb.Tag)
		if tag != nil {
			var err error
			extractor[field], err = makeTagFieldExtractor(field, tag)
			if err != nil {
				return nil, err
			}
		} else {
			if (field.IsMap() && field.MapValue().Kind() == protoreflect.MessageKind) ||
				field.Kind() == protoreflect.MessageKind {
				msgFields = append(msgFields, field)
			}
		}
	}

	// Finally, after getting all of our scalar fields recorded, check any message
	// fields. This will allow recursive messages like:
	//
	//    message Recurse {
	//       Recurse deeper = 1;
	//       optional string tagged = 2 [(turboci.tag).key_scope = EDGE];
	//    }
	//
	// To work correctly.
	for _, field := range msgFields {
		msgDesc := field.Message()
		if field.IsMap() {
			msgDesc = field.MapValue().Message()
		}
		innerExtractor, err := computeTagExtractorLocked(msgDesc)
		if err != nil {
			entry = tagExtractorPoolEntry{err: err}
			tagExtractorPool[msg] = entry
			return nil, err
		}
		if innerExtractor != nil {
			extractor[field] = &tagFieldExtractor{
				isMap:          field.IsMap(),
				isList:         field.IsList(),
				recurseMessage: innerExtractor,
			}
		}
	}

	// If it turns out that extractor was empty, nil it out.
	if len(extractor) == 0 {
		tagExtractorPool[msg] = tagExtractorPoolEntry{}
	}

	return entry.extractor, entry.err
}

// getTagExtractor returns the tagExtractor for `msg`, or an error.
//
// If the extractor/error for msg has not been computed yet, this will compute
// and cache it as a side effect.
func getTagExtractor(msg protoreflect.MessageDescriptor) (tagExtractor, error) {
	tagExtractorPoolMu.RLock()
	entry, has := tagExtractorPool[msg]
	tagExtractorPoolMu.RUnlock()

	if has {
		return entry.extractor, entry.err
	}

	tagExtractorPoolMu.Lock()
	defer tagExtractorPoolMu.Unlock()
	return computeTagExtractorLocked(msg)
}
