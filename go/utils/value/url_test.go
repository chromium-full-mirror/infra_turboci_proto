// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/types/known/emptypb"
)

func TestURL(t *testing.T) {
	t.Parallel()

	if got, want := URL[*emptypb.Empty](), TypePrefix+"google.protobuf.Empty"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
	if got, want := URLMsg((*emptypb.Empty)(nil)), TypePrefix+"google.protobuf.Empty"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func TestURLPatternPackageOf(t *testing.T) {
	t.Parallel()

	if got, want := URLPatternPackageOf[*emptypb.Empty](), TypePrefix+"google.protobuf.*"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
	if got, want := URLPatternPackageOfMsg((*emptypb.Empty)(nil)), TypePrefix+"google.protobuf.*"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}
