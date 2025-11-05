// Copyright 2025 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Package turbocidesc stores compiled protobuf descriptors of Turbo CI APIs.
//
// These are the same descriptors as in the default protobuf registry, with two
// differences:
//   - They include source info (e.g. comments, line numbers, etc).
//   - They transitively include all dependencies.
//
// This package primarily exists to allow LUCI RPC Explorer to show comments
// in its request editor when working with Turbo CI APIs. Prefer to use
// descriptors from the native protobuf registry instead if possible.
package turbocidesc

import (
	_ "embed"
)

//go:embed desc.pb.gz
var gzipped []byte

// CompressedFileDescriptorSet returns a gzip-compressed serialized
// FileDescriptorSet with all Turbo CI proto files and their transitive
// dependencies.
func CompressedFileDescriptorSet() []byte { return gzipped }
