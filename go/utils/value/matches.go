// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"slices"

	"google.golang.org/protobuf/proto"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// WriteMatchesRef returns true if the ValueWrite and ValueRef have the
// same content (including tags).
//
// `ref` must have a digest.
//
// If `ref` has both `inline` and `digest`, it is the caller's responsibility
// to ensure these match.
func WriteMatchesRef(write *orchestratorpb.ValueWrite, ref *orchestratorpb.ValueRef) bool {
	if write.GetRealm() != ref.GetRealm() || write.GetData().GetTypeUrl() != ref.GetTypeUrl() {
		return false
	}
	if !slices.EqualFunc(write.GetTags(), ref.GetTags(),
		func(a, b *orchestratorpb.Tag) bool { return proto.Equal(a, b) },
	) {
		return false
	}
	if !ref.HasDigest() {
		// ref is invalid as it doesn't have digest set
		return false
	}
	if ref.HasInline() {
		return proto.Equal(write.GetData(), ref.GetInline())
	}
	return string(ComputeDigest(write.GetData())) == ref.GetDigest()
}

// RefMatchesRef returns true if the two refs match (including tags).
//
// If the refs contain inline data, it's the caller's responsibility to ensure
// this matches the refs' digests.
func RefMatchesRef(a, b *orchestratorpb.ValueRef) bool {
	if a.GetRealm() != b.GetRealm() || a.GetTypeUrl() != b.GetTypeUrl() {
		return false
	}

	if !a.HasDigest() || !b.HasDigest() {
		// ValueRefs without digest are invalid.
		return false
	}

	if a.GetDigest() != b.GetDigest() {
		return false
	}

	// Lastly, compare all the tags.
	return slices.EqualFunc(a.GetTags(), b.GetTags(),
		func(a, b *orchestratorpb.Tag) bool { return proto.Equal(a, b) },
	)
}
