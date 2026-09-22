// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"errors"
	"strings"
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
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
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	t.Run(`want_binary_inline`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))
		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason(0) {
			t.Errorf("got OmitReason %v, want 0", got)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}
	})

	t.Run(`want_binary_remote`, func(t *testing.T) {
		mSrc := SimpleDataSource{}
		ref := makeRef(t, mSrc, structpb.NewBoolValue(true))
		dgst := "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetDigest(); got != dgst {
			t.Errorf("got digest %q, want %q", got, dgst)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}
	})

	t.Run(`want_json_inline`, func(t *testing.T) {
		lst, err := structpb.NewList([]any{true})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		ref := makeRef(t, nil, lst)

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason(0) {
			t.Errorf("got OmitReason %v, want 0", got)
		}
		if !wantJSON {
			t.Errorf("expected wantJSON to be true")
		}
	})

	t.Run(`want_json_remote`, func(t *testing.T) {
		mSrc := SimpleDataSource{}
		lst, err := structpb.NewList([]any{true})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		ref := makeRef(t, mSrc, lst)
		dgst := "TiL2hG12z5bCnO-q4sXjaMqObIM7ZeZNAYcHd56bTRE1AQ"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason(0) {
			t.Errorf("got OmitReason %v, want 0", got)
		}
		if !wantJSON {
			t.Errorf("expected wantJSON to be true")
		}

		if got := ref.GetDigest(); got != dgst {
			t.Errorf("got digest %q, want %q", got, dgst)
		}
	})

	t.Run(`want_no_access`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		filter, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, func(realm string) (bool, error) {
			return false, nil
		})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS {
			t.Errorf("got OmitReason %v, want %v", got, orchestratorpb.OmitReason_OMIT_REASON_NO_ACCESS)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}

		if ref.HasDigest() {
			t.Errorf("expected ref.HasDigest() to be false")
		}
		if ref.HasInline() {
			t.Errorf("expected ref.HasInline() to be false")
		}
	})

	t.Run(`unwant_structural_inline`, func(t *testing.T) {
		vf := proto.CloneOf(vf)
		vf.SetIncludeData(nil)

		filter, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason_OMIT_REASON_UNWANTED {
			t.Errorf("got OmitReason %v, want %v", got, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}

		if got, want := ref.GetDigest(), "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ"; got != want {
			t.Errorf("got digest %q, want %q", got, want)
		}
		if ref.HasInline() {
			t.Errorf("expected ref.HasInline() to be false")
		}
	})

	t.Run(`unwant_structural_remote`, func(t *testing.T) {
		vf := proto.CloneOf(vf)
		vf.SetIncludeData(nil)

		filter, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		mSrc := SimpleDataSource{}

		ref := makeRef(t, mSrc, structpb.NewBoolValue(true))

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason_OMIT_REASON_UNWANTED {
			t.Errorf("got OmitReason %v, want %v", got, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}

		if got, want := ref.GetDigest(), "nP03LSTuMLuLfYp94hWnwHOj2kT2Pg_DikrWVQk2tJ4vAQ"; got != want {
			t.Errorf("got digest %q, want %q", got, want)
		}
		if ref.HasInline() {
			t.Errorf("expected ref.HasInline() to be false")
		}
	})

	t.Run(`unwant_type_inline`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))
		ref.SetTypeUrl(TypePrefix + "bogus.namespace.Message")
		ref.GetInline().TypeUrl = TypePrefix + "bogus.namespace.Message"

		wantJSON, err := filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, nil)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if got := ref.GetOmitReason(); got != orchestratorpb.OmitReason_OMIT_REASON_UNWANTED {
			t.Errorf("got OmitReason %v, want %v", got, orchestratorpb.OmitReason_OMIT_REASON_UNWANTED)
		}
		if wantJSON {
			t.Errorf("expected wantJSON to be false")
		}

		if got, want := ref.GetDigest(), "hvSVT6KdvPHO0-h55_J5by3wAe3u5ymMnl0ColX35QkxAQ"; got != want {
			t.Errorf("got digest %q, want %q", got, want)
		}
		if ref.HasInline() {
			t.Errorf("expected ref.HasInline() to be false")
		}
	})

	t.Run(`auth_error`, func(t *testing.T) {
		ref := makeRef(t, nil, structpb.NewBoolValue(true))

		filter, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		_, err = filter.Apply(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS, ref, func(realm string) (bool, error) {
			return false, errors.New("oh no auth exploded")
		})
		if err == nil || !strings.Contains(err.Error(), "oh no auth exploded") {
			t.Fatalf("expected error containing %q, got %v", "oh no auth exploded", err)
		}
	})
}

func TestParseFilter_LegacyFields(t *testing.T) {
	t.Parallel()

	t.Run("legacy_fallback", func(t *testing.T) {
		vf := orchestratorpb.ValueFilter_builder{
			CheckOptions: orchestratorpb.ValueMask_VALUE_MASK_VALUE_TYPE.Enum(),
		}.Build()

		pf, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if !pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected needData to have CHECK_OPTION")
		}
		if !pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_EDIT_REASON_DETAIL) {
			t.Errorf("expected needData to have STAGE_EDIT_REASON_DETAIL")
		}
		if !pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_EDIT_REASON_DETAIL) {
			t.Errorf("expected needData to have CHECK_EDIT_REASON_DETAIL")
		}
	})

	t.Run("include_data_precedence", func(t *testing.T) {
		vf := orchestratorpb.ValueFilter_builder{
			IncludeData:  []orchestratorpb.ValueSlot{orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS},
			CheckOptions: orchestratorpb.ValueMask_VALUE_MASK_VALUE_TYPE.Enum(),
		}.Build()

		pf, err := ParseFilter(vf)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if !pf.needData.HasAll(orchestratorpb.ValueSlot_VALUE_SLOT_STAGE_ARGS) {
			t.Errorf("expected needData to have STAGE_ARGS")
		}
		if pf.needData.HasAny(orchestratorpb.ValueSlot_VALUE_SLOT_CHECK_OPTION) {
			t.Errorf("expected needData not to have CHECK_OPTION")
		}
	})
}
