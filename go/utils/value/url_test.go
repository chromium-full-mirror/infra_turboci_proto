// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/types/known/emptypb"

	"go.chromium.org/turboci/proto/go/internal/test/assert"
)

func TestURL(t *testing.T) {
	t.Parallel()

	assert.Equal(t, TypePrefix+"google.protobuf.Empty", URL[*emptypb.Empty]())
	assert.Equal(t, TypePrefix+"google.protobuf.Empty", URLMsg((*emptypb.Empty)(nil)))
}

func TestURLPatternPackageOf(t *testing.T) {
	t.Parallel()

	assert.Equal(t, TypePrefix+"google.protobuf.*", URLPatternPackageOf[*emptypb.Empty]())
	assert.Equal(t, TypePrefix+"google.protobuf.*", URLPatternPackageOfMsg((*emptypb.Empty)(nil)))
}
