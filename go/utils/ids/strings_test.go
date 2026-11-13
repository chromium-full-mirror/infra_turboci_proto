// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"errors"
	"slices"
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	tofromstringvectorspb "go.chromium.org/turboci/proto/go/testing/vectors/ids/to_from_string"
	"go.chromium.org/turboci/proto/go/utils/internal/test_vector"
)

func assertIdent[I Identifier](t *testing.T, tc *tofromstringvectorspb.ToFromString, id I) {
	t.Helper()

	output := tc.GetOutput()
	wantStr := tc.GetInput()

	if diff := cmp.Diff(output.GetParsed(), Wrap(id), protocmp.Transform()); diff != "" {
		t.Errorf("Wrap(%T) mismatch (-want +got):\n%s", id, diff)
	}
	if got := ToString(id); got != wantStr {
		t.Errorf("ToString(%T) = %q, want %q", id, got, wantStr)
	}
	if got, err := ToStringErr(id); err != nil || got != wantStr {
		t.Errorf("ToStringErr(%T) = (%q, %v), want (%q, nil)", id, got, err, wantStr)
	}
	if got := KindOf(id); got != output.GetKind() {
		t.Errorf("KindOf(%T) = %v, want %v", id, got, output.GetKind())
	}
	wp, chk, stg := Root(id)
	wantRoot := output.GetRoot()
	if diff := cmp.Diff(wantRoot.GetWorkPlan(), wp, protocmp.Transform()); diff != "" {
		t.Errorf("Root(%T) work_plan mismatch (-want +got):\n%s", id, diff)
	}
	if diff := cmp.Diff(wantRoot.GetCheck(), chk, protocmp.Transform()); diff != "" {
		t.Errorf("Root(%T) check mismatch (-want +got):\n%s", id, diff)
	}
	if diff := cmp.Diff(wantRoot.GetStage(), stg, protocmp.Transform()); diff != "" {
		t.Errorf("Root(%T) stage mismatch (-want +got):\n%s", id, diff)
	}
}

type variantCheck func(t *testing.T, tc *tofromstringvectorspb.ToFromString, ident *idspb.Identifier) bool

func checkVariant[I Identifier](get func(*idspb.Identifier) I) variantCheck {
	return func(t *testing.T, tc *tofromstringvectorspb.ToFromString, ident *idspb.Identifier) bool {
		t.Helper()
		v := get(ident)
		if v == nil {
			return false
		}
		assertIdent(t, tc, v)
		return true
	}
}

var variantChecks = []variantCheck{
	checkVariant((*idspb.Identifier).GetWorkPlan),
	checkVariant((*idspb.Identifier).GetCheck),
	checkVariant((*idspb.Identifier).GetCheckResult),
	checkVariant((*idspb.Identifier).GetCheckEdit),
	checkVariant((*idspb.Identifier).GetStage),
	checkVariant((*idspb.Identifier).GetStageAttempt),
	checkVariant((*idspb.Identifier).GetStageEdit),
}

func TestToFromString(t *testing.T) {
	t.Parallel()

	typeFields := (&idspb.Identifier{}).ProtoReflect().Descriptor().Oneofs().ByName("type").Fields().Len()
	if len(variantChecks) != typeFields {
		t.Fatalf("variantChecks has %d entries, but Identifier.type oneof has %d fields", len(variantChecks), typeFields)
	}

	test_vector.Run(t, _TO_FROM_STRING_VECTORS, func(t *testing.T, tc *tofromstringvectorspb.ToFromString) {
		input := tc.GetInput()
		output := tc.GetOutput()

		ident, err := FromString(input)
		if output.GetErr() {
			if err == nil {
				t.Fatalf("expected error, got %v", ident)
			}
			return
		}
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if diff := cmp.Diff(output.GetParsed(), ident, protocmp.Transform()); diff != "" {
			t.Errorf("FromString(%q) mismatch (-want +got):\n%s", input, diff)
		}

		assertIdent(t, tc, ident)
		ok := slices.ContainsFunc(variantChecks, func(fn variantCheck) bool {
			return fn(t, tc, ident)
		})
		if !ok {
			t.Fatalf("unhandled identifier variant: %v", ident.WhichType())
		}
	})
}

func TestToString_edgeCases(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name string
		got  string
		want string
	}{
		{"nil", ToString[*idspb.Check](nil), "<turboci invalid identifier: id was nil>"},
		{"empty_identifier", ToString(&idspb.Identifier{}), "<turboci invalid identifier: id could not be unwrapped>"},
		{"empty_workplan", ToString(&idspb.WorkPlan{}), "<turboci invalid identifier: id was empty>"},
		{"empty_workplan_id", ToString(idspb.WorkPlan_builder{Id: proto.String("")}.Build()), "<turboci invalid identifier: id was empty>"},
		{"wrapped_empty_workplan", ToString(Wrap(&idspb.WorkPlan{})), "<turboci invalid identifier: id was empty>"},
		{
			"check_with_empty_workplan",
			ToString(idspb.Check_builder{
				Id:       proto.String("foo"),
				WorkPlan: &idspb.WorkPlan{},
			}.Build()),
			":Cfoo",
		},
		{
			"wrapped_check_with_empty_workplan_id",
			ToString(Wrap(idspb.Check_builder{
				Id:       proto.String("foo"),
				WorkPlan: idspb.WorkPlan_builder{Id: proto.String("")}.Build(),
			}.Build())),
			":Cfoo",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if tc.got != tc.want {
				t.Errorf("got %q, want %q", tc.got, tc.want)
			}
		})
	}
}

func TestToStringErr_edgeCases(t *testing.T) {
	t.Parallel()

	errCases := []struct {
		name string
		call func() (string, error)
	}{
		{"nil", func() (string, error) { return ToStringErr[*idspb.Check](nil) }},
		{"empty_identifier", func() (string, error) { return ToStringErr(&idspb.Identifier{}) }},
		{"empty_workplan", func() (string, error) { return ToStringErr(&idspb.WorkPlan{}) }},
		{
			"empty_workplan_id",
			func() (string, error) {
				return ToStringErr(idspb.WorkPlan_builder{Id: proto.String("")}.Build())
			},
		},
		{"wrapped_empty_workplan", func() (string, error) { return ToStringErr(Wrap(&idspb.WorkPlan{})) }},
	}

	for _, tc := range errCases {
		t.Run(tc.name, func(t *testing.T) {
			got, err := tc.call()
			if !errors.Is(err, ErrInvalidIdentifier) {
				t.Errorf("got (%q, %v), want ErrInvalidIdentifier", got, err)
			}
		})
	}

	okCases := []struct {
		name string
		call func() (string, error)
		want string
	}{
		{
			"check_with_empty_workplan",
			func() (string, error) {
				return ToStringErr(idspb.Check_builder{
					Id:       proto.String("foo"),
					WorkPlan: &idspb.WorkPlan{},
				}.Build())
			},
			":Cfoo",
		},
		{
			"wrapped_check_with_empty_workplan_id",
			func() (string, error) {
				return ToStringErr(Wrap(idspb.Check_builder{
					Id:       proto.String("foo"),
					WorkPlan: idspb.WorkPlan_builder{Id: proto.String("")}.Build(),
				}.Build()))
			},
			":Cfoo",
		},
	}

	for _, tc := range okCases {
		t.Run(tc.name, func(t *testing.T) {
			got, err := tc.call()
			if err != nil || got != tc.want {
				t.Errorf("got (%q, %v), want (%q, nil)", got, err, tc.want)
			}
		})
	}
}
