// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"errors"
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func shouldWrap[I Identifier](ident I, err error) (*idspb.Identifier, error) {
	if err != nil {
		return nil, err
	}
	return Wrap(ident), nil
}

func TestToFromString(t *testing.T) {
	t.Parallel()

	type testCase struct {
		expect  string
		mkIdent func() (*idspb.Identifier, error)
		kind    idspb.IdentifierKind
	}

	tcs := []testCase{
		{
			":Cmeep",
			func() (*idspb.Identifier, error) {
				return shouldWrap(CheckErr("meep"))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_CHECK,
		},
		{
			":Cmeep:R2", func() (*idspb.Identifier, error) {
				return shouldWrap(CheckResultErr("meep", 2))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_RESULT,
		},
		{
			":Cmeep:V12345/6789",
			func() (*idspb.Identifier, error) {
				ts := time.Unix(12345, 6789)
				return shouldWrap(CheckEditErr("meep", ts))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_EDIT,
		},
		{
			":Smeep",
			func() (*idspb.Identifier, error) {
				return shouldWrap(StageErr(StageNotWorknode, "meep"))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE,
		},
		{
			":?meep",
			func() (*idspb.Identifier, error) {
				return shouldWrap(StageErr(StageIsUnknown, "meep"))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE,
		},
		{
			":Nmeep",
			func() (*idspb.Identifier, error) {
				return shouldWrap(StageErr(StageIsWorknode, "meep"))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE,
		},
		{
			":Smeep:A2",
			func() (*idspb.Identifier, error) {
				return shouldWrap(StageAttemptErr(StageNotWorknode, "meep", 2))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_ATTEMPT,
		},
		{
			":Nmeep:A2",
			func() (*idspb.Identifier, error) {
				return shouldWrap(StageAttemptErr(StageIsWorknode, "meep", 2))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_ATTEMPT,
		},
		{
			":Smeep:V12345/6789",
			func() (*idspb.Identifier, error) {
				ts := time.Unix(12345, 6789)
				return shouldWrap(StageEditErr(StageNotWorknode, "meep", ts))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_EDIT,
		},
		{
			":Nmeep:V12345/6789",
			func() (*idspb.Identifier, error) {
				ts := time.Unix(12345, 6789)
				return shouldWrap(StageEditErr(StageIsWorknode, "meep", ts))
			},
			idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_EDIT,
		},
	}

	for _, tc := range tcs {
		t.Run(tc.expect, func(t *testing.T) {
			t.Parallel()
			id, err := tc.mkIdent()
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got := ToString(id); got != tc.expect {
				t.Errorf("ToString(id) = %q, want %q", got, tc.expect)
			}
			if got, err := ToStringErr(id); err != nil || got != tc.expect {
				t.Errorf("ToStringErr(id) = (%q, %v), want (%q, nil)", got, err, tc.expect)
			}

			if got := KindOf(id); got != tc.kind {
				t.Errorf("KindOf(id) = %v, want %v", got, tc.kind)
			}

			ident, err := FromString(tc.expect)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if diff := cmp.Diff(id, ident, protocmp.Transform()); diff != "" {
				t.Errorf("mismatch (-want +got):\n%s", diff)
			}
		})

		const wp = "00012345"
		wpExpect := "L" + wp + tc.expect
		t.Run(wpExpect, func(t *testing.T) {
			t.Parallel()
			id, err := tc.mkIdent()
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			_, err = SetWorkplanErr(id, wp)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got := ToString(id); got != wpExpect {
				t.Errorf("ToString(id) = %q, want %q", got, wpExpect)
			}
			if got, err := ToStringErr(id); err != nil || got != wpExpect {
				t.Errorf("ToStringErr(id) = (%q, %v), want (%q, nil)", got, err, wpExpect)
			}

			ident, err := FromString(wpExpect)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if diff := cmp.Diff(id, ident, protocmp.Transform()); diff != "" {
				t.Errorf("mismatch (-want +got):\n%s", diff)
			}
		})
	}
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
