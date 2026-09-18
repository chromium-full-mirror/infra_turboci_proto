// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package assert

import (
	"fmt"
	"reflect"
	"strings"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/testing/protocmp"
)

// NoErr fails the test fatally if err is not nil.
func NoErr(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
}

// ErrLike fails the test fatally if err is nil or does not contain the
// expected substring.
func ErrLike(t *testing.T, err error, substr string) {
	t.Helper()
	if err == nil {
		t.Fatalf("Expected error containing %q, got nil", substr)
	}
	if !strings.Contains(err.Error(), substr) {
		t.Fatalf("Expected error containing %q, got: %v", substr, err)
	}
}

// Equal fails the test if got != want (using simple comparison).
func Equal[T comparable](t *testing.T, want, got T) {
	t.Helper()
	if got != want {
		t.Errorf("Mismatch:\nwant: %v\ngot:  %v", want, got)
	}
}

// DefaultOptions will be added to the options in Match.
//
// Only update this at init()-time. Updating this while tests run is likely
// to cause a data race.
var DefaultOptions []cmp.Option

// Match fails the test if got and want do not match.
// It uses go-cmp and automatically handles proto messages correctly.
// Additional cmp.Options can be passed (e.g., protocmp.IgnoreUnknown()).
func Match(t *testing.T, want, got any, opts ...cmp.Option) {
	t.Helper()
	allOpts := append([]cmp.Option{protocmp.Transform()}, opts...)
	allOpts = append(allOpts, DefaultOptions...)
	if diff := cmp.Diff(want, got, allOpts...); diff != "" {
		t.Errorf("Mismatch (-want +got):\n%s", diff)
	}
}

// True fails the test if val is false.
func True(t *testing.T, val bool) {
	t.Helper()
	if !val {
		t.Error("Expected true, got false")
	}
}

// False fails the test if val is true.
func False(t *testing.T, val bool) {
	t.Helper()
	if val {
		t.Error("Expected false, got true")
	}
}

// Nil fails the test if val is not nil.
func Nil(t *testing.T, val any) {
	t.Helper()
	if !isNil(val) {
		t.Errorf("Expected nil, got: %v", val)
	}
}

// Len fails the test if the length of got is not want.
func Len[T any](t *testing.T, got []T, want int) {
	t.Helper()
	if len(got) != want {
		t.Errorf("Expected length %d, got %d: %v", want, len(got), got)
	}
}

// Empty fails the test if got is not empty.
func Empty[T any](t *testing.T, got []T) {
	t.Helper()
	if len(got) != 0 {
		t.Errorf("Expected empty, got length %d: %v", len(got), got)
	}
}

// PanicLike fails the test if f does not panic or if the panic value
// (formatted as a string) does not contain substr.
func PanicLike(t *testing.T, f func(), substr string) {
	t.Helper()
	defer func() {
		r := recover()
		if r == nil {
			t.Fatalf("Expected panic containing %q, got none", substr)
		}
		rStr := fmt.Sprint(r)
		if !strings.Contains(rStr, substr) {
			t.Fatalf("Expected panic containing %q, got: %v", substr, r)
		}
	}()
	f()
}

func isNil(i any) bool {
	if i == nil {
		return true
	}
	v := reflect.ValueOf(i)
	switch v.Kind() {
	case reflect.Chan, reflect.Func, reflect.Map, reflect.Pointer,
		reflect.UnsafePointer, reflect.Interface, reflect.Slice:

		return v.IsNil()
	}
	return false
}
