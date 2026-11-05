// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/reflect/protoregistry"
	"google.golang.org/protobuf/types/known/anypb"
)

// RefToWrite copies a ValueRef into a new ValueWrite.
//
// This is useful to copy a ValueRef discovered via a query or read of some
// node into a new node.
//
// This does NOT recompute Tags. If ValueRef has binary data, this mints a new
// ValueWrite directly. If the ValueRef has a JSON representation, this needs
// to re-encode the JSON to binary, and may produce errors.
func RefToWrite(source DataSource, ref *orchestratorpb.ValueRef) (*orchestratorpb.ValueWrite, error) {
	data, err := GetData(source, ref)
	if err != nil {
		return nil, fmt.Errorf("ref cannot be copied: %w", err)
	}
	if data.GetBinary() != nil {
		// We can directly synthesize a new write.
		return orchestratorpb.ValueWrite_builder{
			Data:  data.GetBinary(),
			Realm: proto.String(ref.GetRealm()),
			Tags:  ref.GetTags(),
		}.Build(), nil
	}

	// Otherwise we need to re-encode it.
	mt, err := protoregistry.GlobalTypes.FindMessageByURL(ref.GetTypeUrl())
	if err != nil {
		return nil, fmt.Errorf("ref cannot be copied: error getting descriptor for %q: %w", ref.GetTypeUrl(), err)
	}
	dec := mt.New().Interface()
	err = protojson.Unmarshal([]byte(data.GetJson().GetValue()), dec)
	if err != nil {
		return nil, fmt.Errorf("ref cannot be copied: error unmarshaling JSON representation: %w", err)
	}
	encAny := &anypb.Any{}
	err = anypb.MarshalFrom(encAny, dec, proto.MarshalOptions{Deterministic: true})
	if err != nil {
		return nil, fmt.Errorf("ref cannot be copied: error marshaling decoded JSON representation: %w", err)
	}

	return orchestratorpb.ValueWrite_builder{
		Data:  encAny,
		Realm: proto.String(ref.GetRealm()),
		Tags:  ref.GetTags(),
	}.Build(), nil
}
