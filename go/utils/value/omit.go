// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"fmt"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// Omit sets the OmitReason in this ref.
//
// If the ref has inline data, it's converted to a digest and then dropped.
//
// Otherwise, if the omit reason is NO_ACCESS, this clears the digest and
// inline data.
//
// Will panic on unknown reasons, including the UNKNOWN (0) value.
func Omit(ref *orchestratorpb.ValueRef, reason orchestratorpb.OmitReason) {
	ref.SetOmitReason(reason)

	switch reason {
	case orchestratorpb.OmitReason_OMIT_REASON_UNWANTED:
		if ref.HasInline() {
			ref.SetDigest(string(ComputeDigest(ref.GetInline())))
			ref.ClearInline()
		}

	case orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS:
		ref.ClearDigest()
		ref.ClearInline()

	case orchestratorpb.OmitReason_OMIT_REASON_MISSING:
		// No-op.

	default:
		panic(fmt.Sprintf("unknown OmitReason: %q", reason))
	}
}
