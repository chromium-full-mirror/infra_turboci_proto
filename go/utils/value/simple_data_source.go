// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

// SimpleDataSource implements the simplest possible [DataSource] with no
// synchronization.
//
// Useful to transform a ValueData map from an RPC response into a [DataSource]
// without any extra allocation or overhead.
//
// Directly construct either via allocation, or by casting a compatible
// map type.
//
// If you need a DataSource to persist through multiple calls, or where you
// need multiple readers or writers, consider [SyncDataSource].
type SimpleDataSource map[string]*orchestratorpb.ValueData

var _ DataSource = SimpleDataSource(nil)

// Retrieve implements [DataSource].
func (s SimpleDataSource) Retrieve(digest Digest) *orchestratorpb.ValueData {
	return s[string(digest)]
}

// InternOne implements [DataSource].
func (s SimpleDataSource) Intern(digest Digest, data *orchestratorpb.ValueData) {
	digestS := string(digest)
	s[digestS] = PickData(s[digestS], data)
}

// UpdateFrom implements [DataSource].
func (s SimpleDataSource) UpdateFrom(data map[string]*orchestratorpb.ValueData) {
	for digest, dat := range data {
		s[digest] = PickData(s[digest], dat)
	}
}
