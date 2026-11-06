// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Package test_vector provides a helper for running vectorized proto tests.
package test_vector

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"google.golang.org/protobuf/encoding/prototext"
	"google.golang.org/protobuf/proto"
)

func extractProto[M proto.Message](t testing.TB, path string) M {
	t.Helper()
	var zero M
	ret := zero.ProtoReflect().New().Interface().(M)
	dat, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := prototext.Unmarshal(dat, ret); err != nil {
		t.Fatal(err)
	}
	return ret
}

// Run discovers all `<name>.in.textpb` and `<name>.out.textpb` pairs in
// `vectorsPath`, unmarshals them into `In` and `Out` proto messages, and invokes
// `cb` inside a parallel `t.Run("<name>", ...)` subtest for each vector.
//
// Note: Takes `*testing.T` rather than `testing.TB` because `testing.TB` does
// not provide `Run` or `Parallel`.
func Run[T proto.Message](t *testing.T, vectorsPath string, cb func(t *testing.T, testCase T)) {
	t.Helper()

	cwd, err := os.Getwd()
	if err != nil {
		t.Fatalf("could not get current working dir: %s", err)
	}
	repoRoot, err := filepath.Abs(cwd)
	if err != nil {
		t.Fatalf("could not abs(%q): %s", cwd, err)
	}
	// Find LICENSE file as a sentinel for the repo root.
	for {
		canary := filepath.Join(repoRoot, "LICENSE")
		_, err := os.Stat(canary)
		if err == nil {
			break
		} else if os.IsNotExist(err) {
			// pass
		} else {
			t.Fatalf("could not stat(%q): %s", canary, err)
		}

		parent := filepath.Dir(repoRoot)
		if parent == repoRoot {
			t.Fatal("could not find repo root LICENSE file")
		}
		repoRoot = parent
	}

	baseDir := filepath.Join(repoRoot, "testing", "vectors", vectorsPath)
	entries, err := os.ReadDir(baseDir)
	if err != nil {
		t.Fatal(err)
	}
	found := false
	for _, item := range entries {
		if base, ok := strings.CutSuffix(item.Name(), ".textpb"); ok {
			found = true
			t.Run(base, func(t *testing.T) {
				t.Parallel()
				cb(t, extractProto[T](t, filepath.Join(baseDir, item.Name())))
			})
		}
	}
	if !found {
		t.Fatalf("no *.textpb files found in %q", vectorsPath)
	}
}
