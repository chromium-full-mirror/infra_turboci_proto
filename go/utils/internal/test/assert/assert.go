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

// option is an internal type which can apply to assertion functions.
//
// Right now the only thing it can do is adjust the msg+args of e.g. t.Errorf.
//
// If this vestigial assertion library ever grows any other options, this can
// be changed.
type option func(msg string, args []any) (string, []any)

// Explain allows you to add an additional explanation to some assertion, e.g.
//
//	assert.True(t, something, assert.Explain("the widget was gnarly: %s", widget))
//
// Would add a new line:
//
//	Because: the widget was gnarly: <the widget>
//
// If the assertion fails.
func Explain(exMsg string, exArgs ...any) option {
	return func(msg string, args []any) (string, []any) {
		return msg + "\nBecause: " + exMsg, append(args, exArgs...)
	}
}

type options []option

func (opts options) apply(msg string, args []any) (string, []any) {
	for _, o := range opts {
		if o == nil {
			continue
		}
		msg, args = o(msg, args)
	}
	return msg, args
}

func fatalf(t *testing.T, opts options, msg string, args ...any) {
	t.Helper()
	msg, args = opts.apply(msg, args)
	t.Fatalf(msg, args...)
}

func errorf(t *testing.T, opts options, msg string, args ...any) {
	t.Helper()
	msg, args = opts.apply(msg, args)
	t.Errorf(msg, args...)
}

// NoErr fails the test fatally if err is not nil.
func NoErr(t *testing.T, err error, opts ...option) {
	t.Helper()
	if err != nil {
		fatalf(t, opts, "Unexpected error: %v", err)
	}
}

// ErrLike fails the test fatally if err is nil or does not contain the
// expected substring.
func ErrLike(t *testing.T, err error, substr string, opts ...option) {
	t.Helper()
	if err == nil {
		fatalf(t, opts, "Expected error containing %q, got nil", substr)
	}
	if !strings.Contains(err.Error(), substr) {
		fatalf(t, opts, "Expected error containing %q, got %v", substr, err)
	}
}

// Equal fails the test if got != want (using simple comparison).
func Equal[T comparable](t *testing.T, want, got T, opts ...option) {
	t.Helper()
	if got != want {
		errorf(t, opts, "Mismatch:\nwant: %v\ngot:  %v", want, got)
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
func Match(t *testing.T, want, got any, cmpOpts ...cmp.Option) bool {
	t.Helper()
	allOpts := append([]cmp.Option{protocmp.Transform()}, cmpOpts...)
	allOpts = append(allOpts, DefaultOptions...)
	if diff := cmp.Diff(want, got, allOpts...); diff != "" {
		t.Errorf("Mismatch (-want +got):\n%s", diff)
		return false
	}
	return true
}

// True fails the test if val is false.
func True(t *testing.T, val bool, opts ...option) bool {
	t.Helper()
	if !val {
		errorf(t, opts, "Expected true, got false")
	}
	return val
}

// False fails the test if val is true.
func False(t *testing.T, val bool, opts ...option) bool {
	t.Helper()
	if val {
		errorf(t, opts, "Expected false, got true")
	}
	return !val
}

// Nil fails the test if val is not nil.
func Nil(t *testing.T, val any, opts ...option) {
	t.Helper()
	if !isNil(val) {
		errorf(t, opts, "Expected nil, got: %v", val)
	}
}

// Len fails the test if the length of got is not want.
func Len[T any](t *testing.T, got []T, want int, opts ...option) {
	t.Helper()
	if len(got) != want {
		errorf(t, opts, "Expected length %d, got %d: %v", want, len(got), got)
	}
}

// Empty fails the test if got is not empty.
func Empty[T any](t *testing.T, got []T, opts ...option) {
	t.Helper()
	if len(got) != 0 {
		errorf(t, opts, "Expected empty, got length %d: %v", len(got), got)
	}
}

// PanicLike fails the test if f does not panic or if the panic value
// (formatted as a string) does not contain substr.
func PanicLike(t *testing.T, f func(), substr string, opts ...option) {
	t.Helper()
	defer func() {
		r := recover()
		if r == nil {
			errorf(t, opts, "Expected panic containing %q, got none", substr)
		}
		rStr := fmt.Sprint(r)
		if !strings.Contains(rStr, substr) {
			errorf(t, opts, "Expected panic containing %q, got: %v", substr, r)
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
