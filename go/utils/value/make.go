// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"google.golang.org/protobuf/proto"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// Inline returns a ValueRef (with inline data).
func Inline(msg proto.Message, realm string) (*orchestratorpb.ValueRef, error) {
	vw, err := Write(msg, realm)
	if err != nil {
		return nil, err
	}
	return InlineRef(vw), nil
}

// MustInline is the same as [Inline], except that it panics on error (i.e. if
// `msg` cannot be marshaled.
func MustInline(msg proto.Message, realm string) *orchestratorpb.ValueRef {
	ret, err := Inline(msg, realm)
	if err != nil {
		panic(err)
	}
	return ret
}

// AbsorbInline consumes the inline data in `ref` into `src`.
//
// Mutates `ref` to set `digest` in place of `inline`.
//
// No-op to absorb digest-based refs.
func AbsorbInline(src DataSource, ref *orchestratorpb.ValueRef) {
	if !ref.HasInline() {
		return
	}
	bin := ref.GetInline()
	dgst := ComputeDigest(bin)
	src.Intern(dgst, orchestratorpb.ValueData_builder{
		Binary: bin,
	}.Build())
	ref.SetDigest(string(dgst))
	ref.ClearInline()
}
