// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"google.golang.org/protobuf/proto"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// InlineRef returns an inline ValueRef which corresponds to `vw`.
//
// This is roughly equivalent to [Inline] when given a message and a realm,
// except that this is a purely mechanical proto message assembly which cannot
// error.
//
// Tags are assumed to be immutable and are copied by pointer, not cloned.
func InlineRef(vw *orchestratorpb.ValueWrite) *orchestratorpb.ValueRef {
	dgst := ComputeDigest(vw.GetData())
	return orchestratorpb.ValueRef_builder{
		TypeUrl: proto.String(vw.GetData().GetTypeUrl()),
		Realm:   proto.String(vw.GetRealm()),
		Inline:  vw.GetData(),
		Digest:  proto.String(string(dgst)),
		Tags:    vw.GetTags(),
	}.Build()
}
