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
// If `ref` has a digest, this will compute a digest for `write`.
func WriteMatchesRef(write *orchestratorpb.ValueWrite, ref *orchestratorpb.ValueRef) bool {
	if write.GetRealm() != ref.GetRealm() || write.GetData().GetTypeUrl() != ref.GetTypeUrl() {
		return false
	}
	if !slices.EqualFunc(write.GetTags(), ref.GetTags(),
		func(a, b *orchestratorpb.Tag) bool { return proto.Equal(a, b) },
	) {
		return false
	}
	if ref.HasInline() {
		return proto.Equal(write.GetData(), ref.GetInline())
	}
	return string(ComputeDigest(write.GetData())) == ref.GetDigest()
}

// RefMatchesRef returns true if the two refs match (including tags).
func RefMatchesRef(a, b *orchestratorpb.ValueRef) bool {
	if a.GetRealm() != b.GetRealm() || a.GetTypeUrl() != b.GetTypeUrl() {
		return false
	}

	if !slices.EqualFunc(a.GetTags(), b.GetTags(),
		func(a, b *orchestratorpb.Tag) bool { return proto.Equal(a, b) },
	) {
		return false
	}

	const A = 0
	const B = 1
	inline := []bool{a.HasInline(), b.HasInline()}
	digest := []bool{a.HasDigest(), b.HasDigest()}

	switch {
	case inline[A] && inline[B]:
		return proto.Equal(a.GetInline(), b.GetInline())

	case inline[A] && digest[B]:
		return string(ComputeDigest(a.GetInline())) == b.GetDigest()

	case digest[A] && inline[B]:
		return a.GetDigest() == string(ComputeDigest(b.GetInline()))

	case digest[A] && digest[B]:
		return a.GetDigest() == b.GetDigest()
	}

	return false
}
