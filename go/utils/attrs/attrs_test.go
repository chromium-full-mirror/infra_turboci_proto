// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package attrs

import (
	"strings"
	"testing"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func mustStageAttr(t testing.TB, name, expression string, args ...StageAttributeArg) *orchestratorpb.WriteNodesRequest_StageAttributeWrite {
	t.Helper()
	attr, err := StageAttribute(name, expression, args...)
	if err != nil {
		t.Fatalf("unexpected error creating stage attribute: %v", err)
	}
	return attr
}

func mustCheckAttr(t testing.TB, name, expression string, args ...CheckAttributeArg) *orchestratorpb.WriteNodesRequest_CheckAttributeWrite {
	t.Helper()
	attr, err := CheckAttribute(name, expression, args...)
	if err != nil {
		t.Fatalf("unexpected error creating check attribute: %v", err)
	}
	return attr
}

func TestStageAttribute(t *testing.T) {
	t.Parallel()

	t.Run("leaves_on_state_unset_without_args", func(t *testing.T) {
		t.Parallel()

		attr, err := StageAttribute("my_team.metric", "tags.stage.args.hasKey('env')")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		want := orchestratorpb.WriteNodesRequest_StageAttributeWrite_builder{
			Name:       proto.String("my_team.metric"),
			Expression: proto.String("tags.stage.args.hasKey('env')"),
		}.Build()

		if diff := cmp.Diff(want, attr, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
		if attr.HasOnState() {
			t.Errorf("expected OnState to be unset, got %v", attr.GetOnState())
		}
	})

	t.Run("rejects_unknown_state", func(t *testing.T) {
		t.Parallel()

		_, err := StageAttribute("my_team.metric", "tags.stage.args.hasKey('env')", WithStageOnState(orchestratorpb.StageState_STAGE_STATE_UNKNOWN))
		if err == nil {
			t.Fatal("expected error, got nil")
		}
		if !strings.Contains(err.Error(), "invalid stage state") {
			t.Errorf("expected 'invalid stage state' error, got: %v", err)
		}
	})

	t.Run("preserves_explicit_state", func(t *testing.T) {
		t.Parallel()

		states := []orchestratorpb.StageState{
			orchestratorpb.StageState_STAGE_STATE_PLANNED,
			orchestratorpb.StageState_STAGE_STATE_ATTEMPTING,
			orchestratorpb.StageState_STAGE_STATE_AWAITING_GROUP,
			orchestratorpb.StageState_STAGE_STATE_FINAL,
		}

		for _, state := range states {
			attr, err := StageAttribute("my_team.metric", "true", WithStageOnState(state))
			if err != nil {
				t.Fatalf("unexpected error for state %v: %v", state, err)
			}
			if attr.GetOnState() != state {
				t.Errorf("got on_state %v, want %v", attr.GetOnState(), state)
			}
		}
	})

	t.Run("sets_optional_attribute_type", func(t *testing.T) {
		t.Parallel()

		types := []orchestratorpb.AttributeType{
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL,
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL_LIST,
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64,
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64_LIST,
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_STRING,
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_STRING_LIST,
		}

		for _, attrType := range types {
			attr, err := StageAttribute("my_team.metric", "true", WithAttributeType(attrType))
			if err != nil {
				t.Fatalf("unexpected error for type %v: %v", attrType, err)
			}
			if attr.GetAttributeType() != attrType {
				t.Errorf("got attribute_type %v, want %v", attr.GetAttributeType(), attrType)
			}
		}
	})

	t.Run("applies_multiple_valid_args", func(t *testing.T) {
		t.Parallel()

		attr, err := StageAttribute(
			"my_team.metric",
			"true",
			WithStageOnState(orchestratorpb.StageState_STAGE_STATE_PLANNED),
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL),
		)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if attr.GetOnState() != orchestratorpb.StageState_STAGE_STATE_PLANNED {
			t.Errorf("got on_state %v, want %v", attr.GetOnState(), orchestratorpb.StageState_STAGE_STATE_PLANNED)
		}
		if attr.GetAttributeType() != orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL {
			t.Errorf("got attribute_type %v, want %v", attr.GetAttributeType(), orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL)
		}
	})

	t.Run("rejects_empty_expression", func(t *testing.T) {
		t.Parallel()

		_, err := StageAttribute("my_team.metric", "")
		if err == nil || !strings.Contains(err.Error(), "expression cannot be empty") {
			t.Fatalf("expected error containing %q, got: %v", "expression cannot be empty", err)
		}
	})

	t.Run("rejects_invalid_state", func(t *testing.T) {
		t.Parallel()

		invalidStates := []orchestratorpb.StageState{
			orchestratorpb.StageState(999),
			orchestratorpb.StageState(-1),
		}

		for _, state := range invalidStates {
			_, err := StageAttribute("my_team.metric", "true", WithStageOnState(state))
			if err == nil || !strings.Contains(err.Error(), "invalid stage state") {
				t.Errorf("expected error containing %q for state %v, got: %v", "invalid stage state", state, err)
			}
		}
	})

	t.Run("rejects_invalid_attribute_type", func(t *testing.T) {
		t.Parallel()

		invalidTypes := []orchestratorpb.AttributeType{
			orchestratorpb.AttributeType_ATTRIBUTE_TYPE_UNKNOWN,
			orchestratorpb.AttributeType(999),
			orchestratorpb.AttributeType(-1),
		}

		for _, attrType := range invalidTypes {
			_, err := StageAttribute("my_team.metric", "true", WithAttributeType(attrType))
			if err == nil || !strings.Contains(err.Error(), "invalid attribute type") {
				t.Errorf("expected error containing %q for type %v, got: %v", "invalid attribute type", attrType, err)
			}
		}
	})

	t.Run("rejects_multiple_attribute_types", func(t *testing.T) {
		t.Parallel()

		_, err := StageAttribute(
			"my_team.metric",
			"true",
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL),
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64),
		)
		wantErr := "attrs: cannot overwrite attribute type ATTRIBUTE_TYPE_BOOL with ATTRIBUTE_TYPE_INT64"
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got: %v", wantErr, err)
		}
	})

	t.Run("rejects_multiple_states", func(t *testing.T) {
		t.Parallel()

		_, err := StageAttribute(
			"my_team.metric",
			"true",
			WithStageOnState(orchestratorpb.StageState_STAGE_STATE_PLANNED),
			WithStageOnState(orchestratorpb.StageState_STAGE_STATE_FINAL),
		)
		wantErr := "attrs: cannot overwrite stage state STAGE_STATE_PLANNED with STAGE_STATE_FINAL"
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got: %v", wantErr, err)
		}
	})
}

func TestCheckAttribute(t *testing.T) {
	t.Parallel()

	t.Run("leaves_on_state_unset_without_args", func(t *testing.T) {
		t.Parallel()

		attr, err := CheckAttribute("my_team.metric", "tags.check.options.hasKey('env')")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		want := orchestratorpb.WriteNodesRequest_CheckAttributeWrite_builder{
			Name:       proto.String("my_team.metric"),
			Expression: proto.String("tags.check.options.hasKey('env')"),
		}.Build()

		if diff := cmp.Diff(want, attr, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
		if attr.HasOnState() {
			t.Errorf("expected OnState to be unset, got %v", attr.GetOnState())
		}
	})

	t.Run("rejects_unknown_state", func(t *testing.T) {
		t.Parallel()

		_, err := CheckAttribute("my_team.metric", "tags.check.options.hasKey('env')", WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_UNKNOWN))
		if err == nil {
			t.Fatal("expected error, got nil")
		}
		if !strings.Contains(err.Error(), "invalid check state") {
			t.Errorf("expected 'invalid check state' error, got: %v", err)
		}
	})

	t.Run("preserves_explicit_state", func(t *testing.T) {
		t.Parallel()

		states := []orchestratorpb.CheckState{
			orchestratorpb.CheckState_CHECK_STATE_PLANNING,
			orchestratorpb.CheckState_CHECK_STATE_PLANNED,
			orchestratorpb.CheckState_CHECK_STATE_WAITING,
			orchestratorpb.CheckState_CHECK_STATE_FINAL,
		}

		for _, state := range states {
			attr, err := CheckAttribute("my_team.metric", "true", WithCheckOnState(state))
			if err != nil {
				t.Fatalf("unexpected error for state %v: %v", state, err)
			}
			if attr.GetOnState() != state {
				t.Errorf("got on_state %v, want %v", attr.GetOnState(), state)
			}
		}
	})

	t.Run("applies_multiple_valid_args", func(t *testing.T) {
		t.Parallel()

		attr, err := CheckAttribute(
			"my_team.metric",
			"true",
			WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_PLANNING),
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64),
		)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if attr.GetOnState() != orchestratorpb.CheckState_CHECK_STATE_PLANNING {
			t.Errorf("got on_state %v, want %v", attr.GetOnState(), orchestratorpb.CheckState_CHECK_STATE_PLANNING)
		}
		if attr.GetAttributeType() != orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64 {
			t.Errorf("got attribute_type %v, want %v", attr.GetAttributeType(), orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64)
		}
	})

	t.Run("rejects_invalid_state", func(t *testing.T) {
		t.Parallel()

		invalidStates := []orchestratorpb.CheckState{
			orchestratorpb.CheckState(999),
			orchestratorpb.CheckState(-1),
		}

		for _, state := range invalidStates {
			_, err := CheckAttribute("my_team.metric", "true", WithCheckOnState(state))
			if err == nil || !strings.Contains(err.Error(), "invalid check state") {
				t.Errorf("expected error containing %q for state %v, got: %v", "invalid check state", state, err)
			}
		}
	})

	t.Run("rejects_multiple_states", func(t *testing.T) {
		t.Parallel()

		_, err := CheckAttribute(
			"my_team.metric",
			"true",
			WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_PLANNING),
			WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_FINAL),
		)
		wantErr := "attrs: cannot overwrite check state CHECK_STATE_PLANNING with CHECK_STATE_FINAL"
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got: %v", wantErr, err)
		}
	})

	t.Run("rejects_multiple_attribute_types", func(t *testing.T) {
		t.Parallel()

		_, err := CheckAttribute(
			"my_team.metric",
			"true",
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL),
			WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_STRING),
		)
		wantErr := "attrs: cannot overwrite attribute type ATTRIBUTE_TYPE_BOOL with ATTRIBUTE_TYPE_STRING"
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got: %v", wantErr, err)
		}
	})
}

func TestValidateAttributeName(t *testing.T) {
	t.Parallel()

	t.Run("valid_names", func(t *testing.T) {
		t.Parallel()

		validNames := []string{
			"foo.bar",
			"my_team.my_component.metric_count",
			"a.b",
			"pkg.sub_pkg.name_123",
		}
		for _, name := range validNames {
			if err := validateAttributeName(name); err != nil {
				t.Errorf("unexpected error for valid name %q: %v", name, err)
			}
		}
	})

	t.Run("invalid_names", func(t *testing.T) {
		t.Parallel()

		invalidNames := []struct {
			name    string
			desc    string
			wantErr string
		}{
			{name: "", desc: "empty name", wantErr: "invalid attribute name"},
			{name: "metric", desc: "no dot namespace", wantErr: "invalid attribute name"},
			{name: "my_team.Metric", desc: "uppercase character", wantErr: "invalid attribute name"},
			{name: "My_team.metric", desc: "uppercase namespace", wantErr: "invalid attribute name"},
			{name: "_team.metric", desc: "leading underscore in segment", wantErr: "invalid attribute name"},
			{name: "team._metric", desc: "leading underscore in second segment", wantErr: "invalid attribute name"},
			{name: "1team.metric", desc: "leading digit in segment", wantErr: "invalid attribute name"},
			{name: ".team.metric", desc: "leading dot", wantErr: "invalid attribute name"},
			{name: "team.metric.", desc: "trailing dot", wantErr: "invalid attribute name"},
			{name: "team..metric", desc: "consecutive dots", wantErr: "invalid attribute name"},
			{name: "team.metric-name", desc: "hyphen in name", wantErr: "invalid attribute name"},
			{name: "check.my_attr", desc: "reserved check. prefix", wantErr: "reserved prefix"},
			{name: "stage.my_attr", desc: "reserved stage. prefix", wantErr: "reserved prefix"},
			{name: "tags.my_attr", desc: "reserved tags. prefix", wantErr: "reserved prefix"},
		}

		for _, tc := range invalidNames {
			err := validateAttributeName(tc.name)
			if err == nil || !strings.Contains(err.Error(), tc.wantErr) {
				t.Errorf("[%s] expected error containing %q for name %q, got: %v", tc.desc, tc.wantErr, tc.name, err)
			}
		}
	})
}

func TestAddStageAttributes(t *testing.T) {
	t.Parallel()

	t.Run("appends_and_preserves_existing", func(t *testing.T) {
		t.Parallel()

		a1 := mustStageAttr(t, "my_team.attr1", "true")
		sw := orchestratorpb.WriteNodesRequest_StageWrite_builder{
			Attributes: []*orchestratorpb.WriteNodesRequest_StageAttributeWrite{a1},
		}.Build()

		a2 := mustStageAttr(t, "my_team.attr2", "false")
		if err := AddStageAttributes(sw, a2); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		attrs := sw.GetAttributes()
		if len(attrs) != 2 {
			t.Fatalf("expected 2 attributes, got %d", len(attrs))
		}
		if diff := cmp.Diff([]string{"my_team.attr1", "my_team.attr2"}, []string{attrs[0].GetName(), attrs[1].GetName()}, cmpopts.EquateEmpty()); diff != "" {
			t.Errorf("unexpected attribute names (-want +got):\n%s", diff)
		}
	})

	t.Run("noop_on_zero_attributes", func(t *testing.T) {
		t.Parallel()

		sw := orchestratorpb.WriteNodesRequest_StageWrite_builder{}.Build()
		if err := AddStageAttributes(sw); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if len(sw.GetAttributes()) != 0 {
			t.Errorf("expected 0 attributes, got %d", len(sw.GetAttributes()))
		}
	})

	t.Run("rejects_nil_stage_write", func(t *testing.T) {
		t.Parallel()

		a1 := mustStageAttr(t, "my_team.attr1", "true")
		err := AddStageAttributes(nil, a1)
		if err == nil || !strings.Contains(err.Error(), "stage write cannot be nil") {
			t.Fatalf("expected error containing %q, got: %v", "stage write cannot be nil", err)
		}
	})

	t.Run("rejects_nil_attribute", func(t *testing.T) {
		t.Parallel()

		sw := orchestratorpb.WriteNodesRequest_StageWrite_builder{}.Build()
		err := AddStageAttributes(sw, nil)
		if err == nil || !strings.Contains(err.Error(), "invalid attribute name") {
			t.Fatalf("expected error containing %q, got: %v", "invalid attribute name", err)
		}
	})

	t.Run("rejects_duplicate_matching_existing", func(t *testing.T) {
		t.Parallel()

		a1 := mustStageAttr(t, "my_team.attr1", "true")
		sw := orchestratorpb.WriteNodesRequest_StageWrite_builder{
			Attributes: []*orchestratorpb.WriteNodesRequest_StageAttributeWrite{a1},
		}.Build()

		a2 := mustStageAttr(t, "my_team.attr1", "false")
		err := AddStageAttributes(sw, a2)
		if err == nil || !strings.Contains(err.Error(), `duplicate attribute name "my_team.attr1"`) {
			t.Fatalf("expected error containing %q, got: %v", `duplicate attribute name "my_team.attr1"`, err)
		}
	})
}

func TestAddCheckAttributes(t *testing.T) {
	t.Parallel()

	t.Run("appends_and_preserves_existing", func(t *testing.T) {
		t.Parallel()

		a1 := mustCheckAttr(t, "my_team.attr1", "true")
		cw := orchestratorpb.WriteNodesRequest_CheckWrite_builder{
			Attributes: []*orchestratorpb.WriteNodesRequest_CheckAttributeWrite{a1},
		}.Build()

		a2 := mustCheckAttr(t, "my_team.attr2", "false")
		if err := AddCheckAttributes(cw, a2); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		attrs := cw.GetAttributes()
		if len(attrs) != 2 {
			t.Fatalf("expected 2 attributes, got %d", len(attrs))
		}
		if diff := cmp.Diff([]string{"my_team.attr1", "my_team.attr2"}, []string{attrs[0].GetName(), attrs[1].GetName()}, cmpopts.EquateEmpty()); diff != "" {
			t.Errorf("unexpected attribute names (-want +got):\n%s", diff)
		}
	})

	t.Run("noop_on_zero_attributes", func(t *testing.T) {
		t.Parallel()

		cw := orchestratorpb.WriteNodesRequest_CheckWrite_builder{}.Build()
		if err := AddCheckAttributes(cw); err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if len(cw.GetAttributes()) != 0 {
			t.Errorf("expected 0 attributes, got %d", len(cw.GetAttributes()))
		}
	})

	t.Run("rejects_nil_check_write", func(t *testing.T) {
		t.Parallel()

		a1 := mustCheckAttr(t, "my_team.attr1", "true")
		err := AddCheckAttributes(nil, a1)
		if err == nil || !strings.Contains(err.Error(), "check write cannot be nil") {
			t.Fatalf("expected error containing %q, got: %v", "check write cannot be nil", err)
		}
	})

	t.Run("rejects_nil_attribute", func(t *testing.T) {
		t.Parallel()

		cw := orchestratorpb.WriteNodesRequest_CheckWrite_builder{}.Build()
		err := AddCheckAttributes(cw, nil)
		if err == nil || !strings.Contains(err.Error(), "invalid attribute name") {
			t.Fatalf("expected error containing %q, got: %v", "invalid attribute name", err)
		}
	})

	t.Run("rejects_duplicate_matching_existing", func(t *testing.T) {
		t.Parallel()

		a1 := mustCheckAttr(t, "my_team.attr1", "true")
		cw := orchestratorpb.WriteNodesRequest_CheckWrite_builder{
			Attributes: []*orchestratorpb.WriteNodesRequest_CheckAttributeWrite{a1},
		}.Build()

		a2 := mustCheckAttr(t, "my_team.attr1", "false")
		err := AddCheckAttributes(cw, a2)
		if err == nil || !strings.Contains(err.Error(), `duplicate attribute name "my_team.attr1"`) {
			t.Fatalf("expected error containing %q, got: %v", `duplicate attribute name "my_team.attr1"`, err)
		}
	})
}
