// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"go.chromium.org/turboci/proto/go/utils/tags"
)

// These constants are special values which can be used with [Write].
//
// See the documentation on [orchestratorpb.ValueWrite] for more info.
const (
	// RealmFromToken can be used in place of a concrete realm to instruct the
	// orchestrator to use the realm from the writer's token (e.g. WorkPlan
	// creation token or Stage Attempt token).
	RealmFromToken string = "$from_token"

	// RealmFromContainer can be used in place of a concrete realm to instruct
	// the orchestrator to use the realm from the container where this ValueWrite
	// will be used:
	//   - Checks and Stages are contained in the WorkPlan.
	//   - Check Options, Check Result Data, etc. are contained in their
	//     Check.
	//   - Stage Attempt Details, Stage Attempt Progress Details, etc. are
	//     contained in their Stage.
	//   - Edit Reasons for a Check or Stage are contained in their
	//     respective Edit, which always has the same realm as the Check or
	//     Stage to which the Edit belongs.
	RealmFromContainer string = "$from_container"

	// RealmForLegacyWorkNode can be used in place of a realm to instruct the
	// orchestrator to use legacy work node ACLs instead of realm-based ACLs.
	//
	// Can only be used when writing work node stages. When a stage (or a
	// ValueRef inside of it) is written using this placeholder, the final realm
	// stored in the Stage proto (and ValueRefs) will be empty string.
	//
	// Note that it is allowed to write legacy work nodes with some concrete
	// realm. This will switch their ACLs to be based on realms, but only when
	// accessed via Turbo CI Orchestrator APIs. Access through Workplan API is
	// always governed by legacy ACLs.
	RealmForLegacyWorkNode string = "$legacy_worknode"
)

// Write returns a [ValueWrite] for use with TurboCI write APIs (e.g.
// WriteNodes)
//
// Realm should be a full global realm (e.g. `proj:realm`), or may be one of the
// two special values [RealmFromToken] and [RealmFromContainer].
//
// This can only return an error on a proto marshaling error (e.g. if `msg` is
// nil). If you statically know that this cannot be problematic (e.g. your
// binary is known to have functioning proto support), consider [MustWrite].
//
// `realm` is a SINGULAR optional field. If omitted, RealmFromContainer
// is used. If provided, this will be used as the realm. Providing it multiple
// times is an error.
//
// It is an error to pass a google.protobuf.Any as `msg`; either pass the
// underlying message, or, if this is not possible, directly assemble the
// orchestratorpb.ValueWrite.
//
// This internally calls [tags.ForMessage] to generate tags for `msg`.
func Write(msg proto.Message, realm ...string) (*orchestratorpb.ValueWrite, error) {
	apb, ok := msg.(*anypb.Any)
	if ok {
		return nil, fmt.Errorf("value.Write: cannot handle google.protobuf.Any as `msg`.")
	}

	apb = &anypb.Any{}
	err := anypb.MarshalFrom(apb, msg, proto.MarshalOptions{Deterministic: true})
	if err != nil {
		return nil, fmt.Errorf("value.Write: %w", err)
	}
	actualRealm := RealmFromContainer
	if len(realm) == 1 {
		actualRealm = realm[0]
	} else if len(realm) > 1 {
		return nil, fmt.Errorf("value.Write: realm provided more than once")
	}

	tags, err := tags.ForMessage(msg)
	if err != nil {
		return nil, fmt.Errorf("value.Write: extracting tags: %w", err)
	}

	return orchestratorpb.ValueWrite_builder{
		Data:  apb,
		Realm: &actualRealm,
		Tags:  tags.Proto(),
	}.Build(), nil
}

// MustWrite is like [Write], but panics on error.
//
// Like [Write], `realm` must be provided 0 or 1 times, and defaults to
// RealmFromContainer if omitted.
func MustWrite(msg proto.Message, realm ...string) *orchestratorpb.ValueWrite {
	ret, err := Write(msg, realm...)
	if err != nil {
		panic(err)
	}
	return ret
}

// Writes is the same as [Write], except it processes multiple messages, giving
// them all the same realm.
func Writes(msgs []proto.Message, realm ...string) ([]*orchestratorpb.ValueWrite, error) {
	ret := make([]*orchestratorpb.ValueWrite, len(msgs))
	for i, msg := range msgs {
		var err error
		ret[i], err = Write(msg, realm...)
		if err != nil {
			return nil, err
		}
	}
	return ret, nil
}

// MustWrites is the same as [Writes], except it panics on error.
func MustWrites(msgs []proto.Message, realm ...string) []*orchestratorpb.ValueWrite {
	ret, err := Writes(msgs, realm...)
	if err != nil {
		panic(err)
	}
	return ret
}
