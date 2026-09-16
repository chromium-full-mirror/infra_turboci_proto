// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"
	"iter"
	"maps"
	"sync"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	tagpb "go.chromium.org/turboci/proto/go/tag"
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

// makeSubmessageTagFieldExtractor makes a tagFieldExtractor to recurse into
// the message covered by `extractor`.
//
// Handles repeated fields as well as `map<*, msgType>` fields.
func makeSubmessageTagFieldExtractor(field protoreflect.FieldDescriptor, extractor tagExtractor) *tagFieldExtractor {
	return &tagFieldExtractor{
		isMap:          field.IsMap(),
		isList:         field.IsList(),
		recurseMessage: extractor,
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

	// a nil tagExtractor and nil error indicates that this message doesn't
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
// In particular, this converts the source-annotation friendly tagpb.ReadScope
// to the API orchestratorpb.ReadScope enum, ensures that keyScope is >=
// valueScope, and applies the default index_unset logic for bool fields.
func calculateScopes(tag *tagpb.Tag, kind protoreflect.Kind) (captureUnset bool, keyScope, valueScope orchestratorpb.ReadScope) {
	toReadScope := func(in tagpb.ReadScope) orchestratorpb.ReadScope {
		switch in {
		case tagpb.ReadScope_NODE:
			return orchestratorpb.ReadScope_READ_SCOPE_NODE
		case tagpb.ReadScope_WORK_PLAN:
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
func makeTagFieldExtractor(field protoreflect.FieldDescriptor, tag *tagpb.Tag) (*tagFieldExtractor, error) {
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

// submsgDesc returns the target MessageDescriptor if field is a message field
// or map-to-message field, or nil otherwise.
func submsgDesc(field protoreflect.FieldDescriptor) protoreflect.MessageDescriptor {
	if field.IsMap() {
		if field.MapValue().Kind() == protoreflect.MessageKind {
			return field.MapValue().Message()
		}
		return nil
	}
	if field.Kind() == protoreflect.MessageKind {
		return field.Message()
	}
	return nil
}

// exploreType recursively walks `msg`, adding an entry to `toAdd` which
// describes how to extract all tags (including recursion) for `msg`.
//
// If `msg` is mutually recursive with another type we are exploring, this adds
// it to toConverge to be addressed later in `fixupConvergence`.
func exploreType(
	msg protoreflect.MessageDescriptor,
	toAdd map[protoreflect.MessageDescriptor]tagExtractorPoolEntry,
	toConverge map[protoreflect.FieldDescriptor]protoreflect.MessageDescriptor,
) error {
	// Ensure that `msg` has not already been explored.
	if _, ok := toAdd[msg]; ok {
		return nil
	}

	// Add this so that recursion stops.
	toAdd[msg] = tagExtractorPoolEntry{}

	extractor := tagExtractor{}
	for field := range rangeProtoSeq(msg.Fields()) {
		// First, check if this field is directly tagged.
		tag, _ := proto.GetExtension(field.Options(), tagpb.E_Tag).(*tagpb.Tag)
		if tag != nil {
			fExt, err := makeTagFieldExtractor(field, tag)
			if err != nil {
				return err
			}
			extractor[field] = fExt
			continue
		}

		// Check to see if this field has a message kind.
		sub := submsgDesc(field)
		if sub == nil {
			continue
		}

		// If the message kind is already in the global pool, we can either return
		// its error, incorporate its extractor, or skip it (if the message has
		// no tags and no recursions).
		if entry, has := tagExtractorPool[sub]; has {
			if entry.err != nil {
				return entry.err
			}
			if entry.extractor != nil {
				extractor[field] = makeSubmessageTagFieldExtractor(field, entry.extractor)
			}
			continue
		}

		// If the sub message was *not* in the global pool explore the sub message
		// type.
		if err := exploreType(sub, toAdd, toConverge); err != nil {
			return err
		}

		// If the now-explored type has ANY tagged fields (or known recursions), we
		// can directly set it in our extractor.
		if ext := toAdd[sub]; len(ext.extractor) > 0 {
			extractor[field] = makeSubmessageTagFieldExtractor(field, ext.extractor)
		} else {
			// Otherwise, mark this field as needing convergence.
			toConverge[field] = sub
		}
	}

	// If there are any entries that we know for sure, go ahead and set this in
	// toAdd.
	if len(extractor) > 0 {
		toAdd[msg] = tagExtractorPoolEntry{extractor: extractor}
	}
	return nil
}

// fixupConvergence iterates through `toConverge` fixing up entries in `toAdd`
// until iterating through toConverge yields no changes.
//
// Fixing up an entry includes updating toAdd to indicate that a type does, in
// fact, need to recurse into some other type.
func fixupConvergence(
	toAdd map[protoreflect.MessageDescriptor]tagExtractorPoolEntry,
	toConverge map[protoreflect.FieldDescriptor]protoreflect.MessageDescriptor,
) {
	for siz := len(toConverge) + 1; len(toConverge) < siz; siz = len(toConverge) {
		for field, subMsg := range toConverge {
			if ext := toAdd[subMsg].extractor; ext != nil {
				parentMsg := field.ContainingMessage()
				parentExtractor := toAdd[parentMsg].extractor
				if parentExtractor == nil {
					parentExtractor = tagExtractor{}
					toAdd[parentMsg] = tagExtractorPoolEntry{extractor: parentExtractor}
				}
				parentExtractor[field] = makeSubmessageTagFieldExtractor(field, ext)
				delete(toConverge, field)
			}
		}
	}
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

	if entry, has := tagExtractorPool[msg]; has {
		return entry.extractor, entry.err
	}

	toAdd := map[protoreflect.MessageDescriptor]tagExtractorPoolEntry{}
	toConverge := map[protoreflect.FieldDescriptor]protoreflect.MessageDescriptor{}

	if err := exploreType(msg, toAdd, toConverge); err != nil {
		tagExtractorPool[msg] = tagExtractorPoolEntry{err: err}
		return nil, err
	}

	if len(toConverge) > 0 {
		fixupConvergence(toAdd, toConverge)
	}

	maps.Copy(tagExtractorPool, toAdd)

	entry = tagExtractorPool[msg]
	return entry.extractor, entry.err
}
