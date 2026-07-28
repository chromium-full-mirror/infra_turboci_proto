// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"errors"
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/internal/test/assert"
)

// Tests [filterState.filterRef] by virtue of Stage.Args.
func TestFilterRef(t *testing.T) {
	t.Parallel()

	makeRef := func(t testing.TB, src DataSource, msg proto.Message) *orchestratorpb.ValueRef {
		t.Helper()

		ret := MustInline(msg, "proj:realm")

		if src != nil {
			AbsorbInline(src, ret)
		}

		return ret
	}

	vf := orchestratorpb.ValueFilter_builder{
		TypeInfo: orchestratorpb.TypeInfo_builder{
			// want google.protobuf.*
			Wanted:        TypeSetBuilder{}.WithPackagesOf((*structpb.Value)(nil)).MustBuild(),
			UnknownJsonpb: proto.Bool(true),
			// know google.protobuf.Value
			Known: TypeSetBuilder{}.WithMessages((*structpb.Value)(nil)).MustBuild(),
		}.Build(),
		IncludeData: []orchestratorpb.ValueSlot{orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS},
	}.Build()

	filter, err := ParseFilter(vf)
	assert.NoErr(t, err)

	t.Run(`want_binary_inline`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))
		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason(0), ref.GetOmitReason())
		assert.False(t, wantJSON)
	})

	t.Run(`want_binary_remote`, func(t *testing.T) {
		mSrc := SimpleDataSource{}
		ref := makeRef(t, mSrc, structpb.NewBoolValue(true))
		dgst := "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, dgst, ref.GetDigest())
		assert.False(t, wantJSON)
	})

	t.Run(`want_json_inline`, func(t *testing.T) {
		lst, err := structpb.NewList([]any{true})
		assert.NoErr(t, err)
		ref := makeRef(t, nil, lst)

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason(0), ref.GetOmitReason())
		assert.True(t, wantJSON)
	})

	t.Run(`want_json_remote`, func(t *testing.T) {
		mSrc := SimpleDataSource{}
		lst, err := structpb.NewList([]any{true})
		assert.NoErr(t, err)

		ref := makeRef(t, mSrc, lst)
		dgst := "TiL2hG12z5bCnO-q4sXjaMqObIM7ZeZNAYcHd56bTRE1AQ"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason(0), ref.GetOmitReason())
		assert.True(t, wantJSON)

		assert.Equal(t, dgst, ref.GetDigest())
	})

	t.Run(`want_no_access`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		filter, err := ParseFilter(vf)
		assert.NoErr(t, err)

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, func(realm string) (bool, error) {
			return false, nil
		})
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS, ref.GetOmitReason())
		assert.False(t, wantJSON)

		assert.False(t, ref.HasDigest())
		assert.False(t, ref.HasInline())
	})

	t.Run(`unwant_structural_inline`, func(t *testing.T) {
		vf := proto.CloneOf(vf)
		vf.SetIncludeData(nil)

		filter, err := ParseFilter(vf)
		assert.NoErr(t, err)

		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED, ref.GetOmitReason())
		assert.False(t, wantJSON)

		assert.Equal(t, "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ", ref.GetDigest())
		assert.False(t, ref.HasInline())
	})

	t.Run(`unwant_structural_remote`, func(t *testing.T) {
		vf := proto.CloneOf(vf)
		vf.SetIncludeData(nil)

		filter, err := ParseFilter(vf)
		assert.NoErr(t, err)

		mSrc := SimpleDataSource{}

		ref := makeRef(t, mSrc, structpb.NewBoolValue(true))

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED, ref.GetOmitReason())
		assert.False(t, wantJSON)

		assert.Equal(t, "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ", ref.GetDigest())
		assert.False(t, ref.HasInline())
	})

	t.Run(`unwant_type_inline`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))
		ref.SetTypeUrl(TypePrefix + "bogus.namespace.Message")
		ref.GetInline().TypeUrl = TypePrefix + "bogus.namespace.Message"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		assert.NoErr(t, err)
		assert.Equal(t, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED, ref.GetOmitReason())
		assert.False(t, wantJSON)

		assert.Equal(t, "hvSVT6KdvPHO0-h55_J5by3wAe3u5ymMnl0ColX35QkxAQ", ref.GetDigest())
		assert.False(t, ref.HasInline())
	})

	t.Run(`auth_error`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		filter, err := ParseFilter(vf)
		assert.NoErr(t, err)

		_, err = filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, func(realm string) (bool, error) {
			return false, errors.New("oh no auth exploded")
		})
		assert.ErrLike(t, err, "oh no auth exploded")
	})
}

func TestParseFilter_LegacyFields(t *testing.T) {
	t.Parallel()

	t.Run("legacy_fallback", func(t *testing.T) {
		vf := orchestratorpb.ValueFilter_builder{
			CheckOptions: orchestratorpb.ValueMask_VALUE_MASK_VALUE_TYPE.Enum(),
		}.Build()

		pf, err := ParseFilter(vf)
		assert.NoErr(t, err)
		assert.True(t, pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
		assert.True(t, pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL))
		assert.True(t, pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL))
	})

	t.Run("include_data_precedence", func(t *testing.T) {
		vf := orchestratorpb.ValueFilter_builder{
			IncludeData:  []orchestratorpb.ValueSlot{orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS},
			CheckOptions: orchestratorpb.ValueMask_VALUE_MASK_VALUE_TYPE.Enum(),
		}.Build()

		pf, err := ParseFilter(vf)
		assert.NoErr(t, err)
		assert.True(t, pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS))
		assert.False(t, pf.needData.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION))
	})
}
