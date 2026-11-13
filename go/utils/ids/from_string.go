// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"fmt"
	"strconv"
	"strings"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func requireNonEmpty(trimmed string, errP *error) *string {
	if *errP != nil {
		return nil
	}
	if trimmed == "" {
		*errP = fmt.Errorf("unexpected empty token")
		return nil
	}
	return &trimmed
}

func requireInt(trimmed string, errP *error) *int32 {
	if *errP != nil {
		return nil
	}
	ret, err := strconv.ParseInt(trimmed, 10, 32)
	if err != nil {
		*errP = fmt.Errorf("bad idx %q: %w", trimmed, err)
		return nil
	} else if ret <= 0 {
		*errP = fmt.Errorf("bad idx %q: must be > 0", trimmed)
		return nil
	}
	ret32 := int32(ret)
	return &ret32
}

func requireTs(trimmed string, errP *error) *timestamppb.Timestamp {
	if *errP != nil {
		return nil
	}
	parts := strings.Split(trimmed, "/")
	if len(parts) != 2 {
		*errP = fmt.Errorf("bad timestamp: needed seconds/nanos")
		return nil
	}
	seconds, err := strconv.ParseInt(parts[0], 10, 64)
	if err != nil {
		*errP = fmt.Errorf("bad timestamp: parsing seconds %q: %w", parts[0], err)
		return nil
	}
	nanos, err := strconv.ParseInt(parts[1], 10, 32)
	if err != nil {
		*errP = fmt.Errorf("bad timestamp: parsing nanos %q: %w", parts[1], err)
		return nil
	}
	return &timestamppb.Timestamp{Seconds: seconds, Nanos: int32(nanos)}
}

var keyToIdent map[string]func(toks []string) (proto.Message, error)

func requireIdent[T proto.Message](key string, toks []string, errP *error) T {
	var zero T
	if *errP != nil {
		return zero
	}

	var msg proto.Message
	msg, *errP = keyToIdent[key](toks)
	if *errP != nil || msg == nil {
		return zero
	}

	ret, ok := msg.(T)
	if !ok {
		*errP = fmt.Errorf(
			"expected %q, got %q",
			zero.ProtoReflect().Descriptor().Name(),
			msg.ProtoReflect().Descriptor().Name())
	}
	return ret
}

func init() {
	keyToIdent = map[string]func(toks []string) (ret proto.Message, err error){
		"L": func(toks []string) (ret proto.Message, err error) {
			if toks[0] == "" {
				return nil, nil
			}
			return idspb.WorkPlan_builder{Id: &toks[0]}.Build(), nil
		},

		"LC": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.Check_builder{
				WorkPlan: requireIdent[*idspb.WorkPlan]("L", toks, &err),
				Id:       requireNonEmpty(toks[1], &err),
			}.Build()
			return
		},

		"LCR": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.CheckResult_builder{
				Check: requireIdent[*idspb.Check]("LC", toks, &err),
				Idx:   requireInt(toks[2], &err),
			}.Build()
			return
		},

		"LCV": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.CheckEdit_builder{
				Check:   requireIdent[*idspb.Check]("LC", toks, &err),
				Version: requireTs(toks[2], &err),
			}.Build()
			return
		},

		"L?": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.Stage_builder{
				WorkPlan: requireIdent[*idspb.WorkPlan]("L", toks, &err),
				Id:       requireNonEmpty(toks[1], &err),
			}.Build()
			return
		},

		"LS": func(toks []string) (ret proto.Message, err error) {
			s := requireIdent[*idspb.Stage]("L?", toks, &err)
			if err == nil {
				s.SetIsWorknode(false)
			}
			return s, err
		},

		"LN": func(toks []string) (ret proto.Message, err error) {
			s := requireIdent[*idspb.Stage]("L?", toks, &err)
			if err == nil {
				s.SetIsWorknode(true)
			}
			return s, err
		},

		"L?A": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageAttempt_builder{
				Stage: requireIdent[*idspb.Stage]("L?", toks, &err),
				Idx:   requireInt(toks[2], &err),
			}.Build()
			return
		},

		"LSA": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageAttempt_builder{
				Stage: requireIdent[*idspb.Stage]("LS", toks, &err),
				Idx:   requireInt(toks[2], &err),
			}.Build()
			return
		},

		"LNA": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageAttempt_builder{
				Stage: requireIdent[*idspb.Stage]("LN", toks, &err),
				Idx:   requireInt(toks[2], &err),
			}.Build()
			return
		},

		"L?V": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageEdit_builder{
				Stage:   requireIdent[*idspb.Stage]("L?", toks, &err),
				Version: requireTs(toks[2], &err),
			}.Build()
			return
		},

		"LSV": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageEdit_builder{
				Stage:   requireIdent[*idspb.Stage]("LS", toks, &err),
				Version: requireTs(toks[2], &err),
			}.Build()
			return
		},

		"LNV": func(toks []string) (ret proto.Message, err error) {
			ret = idspb.StageEdit_builder{
				Stage:   requireIdent[*idspb.Stage]("LN", toks, &err),
				Version: requireTs(toks[2], &err),
			}.Build()
			return
		},
	}
}

// FromString converts a canonical string representation of a TurboCI identifier
// into its protobuf message form.
//
// The string format is defined in [identifier.proto].
//
// Returns an error if the string is malformed.
//
// [identifier.proto]: https://chromium.googlesource.com/infra/turboci/proto/+/refs/heads/main/turboci/graph/ids/v1/identifier.proto
func FromString(id string) (*idspb.Identifier, error) {
	toks := strings.Split(id, ":")

	keyBytes := make([]byte, len(toks))
	for i, tok := range toks {
		if len(tok) == 0 {
			if i == 0 && len(toks) > 1 {
				// workplan allowed to be empty
				keyBytes[i] = 'L'
			} else {
				return nil, fmt.Errorf("in %q: token %d was empty?", id, i)
			}
		} else if i == 0 && tok == "L" {
			return nil, fmt.Errorf("in %q: unexpected empty token", id)
		} else {
			keyBytes[i] = tok[0]
			toks[i] = tok[1:]
		}
	}
	key := string(keyBytes)

	fn, ok := keyToIdent[key]
	if !ok {
		return nil, fmt.Errorf("in %q: unexpected key %q", id, key)
	}

	ret, err := fn(toks)
	if err != nil {
		return nil, fmt.Errorf("in %q: %w", id, err)
	}
	return wrap(ret), nil
}
