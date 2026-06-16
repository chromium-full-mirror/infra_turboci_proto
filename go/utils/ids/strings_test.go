// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"testing"
	"time"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	"go.chromium.org/turboci/proto/go/internal/test/assert"
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
			assert.NoErr(t, err)

			assert.Equal(t, tc.expect, ToString(id))

			assert.Equal(t, tc.kind, KindOf(id))

			ident, err := FromString(tc.expect)
			assert.Match(t, id, ident)
		})

		const wp = "00012345"
		wpExpect := "L" + wp + tc.expect
		t.Run(wpExpect, func(t *testing.T) {
			t.Parallel()
			id, err := tc.mkIdent()
			assert.NoErr(t, err)
			_, err = SetWorkplanErr(id, wp)
			assert.NoErr(t, err)

			assert.Equal(t, wpExpect, ToString(id))

			ident, err := FromString(wpExpect)
			assert.Match(t, id, ident)
		})
	}
}

func TestToString_nil(t *testing.T) {
	assert.Equal(t, Invalid, ToString[*idspb.Check](nil))
}
