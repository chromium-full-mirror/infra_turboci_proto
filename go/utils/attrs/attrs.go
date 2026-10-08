// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Package attrs provides helper utilities to construct and validate
// AttributeWrite messages and attach them to StageWrite and CheckWrite nodes.
package attrs

import (
	"errors"
	"fmt"
	"regexp"
	"strings"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

var (
	attrNameRegex    = regexp.MustCompile(`^([a-z][a-z0-9_]*\.)+[a-z][a-z0-9_]*$`)
	reservedPrefixes = []string{"check.", "stage.", "tags."}
)

type stageConfig struct {
	onState       *orchestratorpb.StageState
	attributeType *orchestratorpb.AttributeType
}

type checkConfig struct {
	onState       *orchestratorpb.CheckState
	attributeType *orchestratorpb.AttributeType
}

// StageAttributeArg configures a StageAttributeWrite.
type StageAttributeArg interface {
	applyStage(*stageConfig) error
}

// CheckAttributeArg configures a CheckAttributeWrite.
type CheckAttributeArg interface {
	applyCheck(*checkConfig) error
}

// AttributeArg configures an attribute on either a Stage or Check node.
type AttributeArg interface {
	StageAttributeArg
	CheckAttributeArg
}

type stageStateArg orchestratorpb.StageState

func (s stageStateArg) applyStage(cfg *stageConfig) error {
	if cfg.onState != nil {
		return fmt.Errorf("attrs: cannot overwrite stage state %v with %v", *cfg.onState, orchestratorpb.StageState(s))
	}
	state := orchestratorpb.StageState(s)
	switch state {
	case orchestratorpb.StageState_STAGE_STATE_PLANNED,
		orchestratorpb.StageState_STAGE_STATE_ATTEMPTING,
		orchestratorpb.StageState_STAGE_STATE_AWAITING_GROUP,
		orchestratorpb.StageState_STAGE_STATE_FINAL:
		cfg.onState = &state
		return nil
	default:
		return fmt.Errorf("attrs: invalid stage state: %v", state)
	}
}

// WithStageOnState sets the StageState on which the attribute is evaluated.
func WithStageOnState(state orchestratorpb.StageState) StageAttributeArg {
	return stageStateArg(state)
}

type checkStateArg orchestratorpb.CheckState

func (c checkStateArg) applyCheck(cfg *checkConfig) error {
	if cfg.onState != nil {
		return fmt.Errorf("attrs: cannot overwrite check state %v with %v", *cfg.onState, orchestratorpb.CheckState(c))
	}
	state := orchestratorpb.CheckState(c)
	switch state {
	case orchestratorpb.CheckState_CHECK_STATE_PLANNING,
		orchestratorpb.CheckState_CHECK_STATE_PLANNED,
		orchestratorpb.CheckState_CHECK_STATE_WAITING,
		orchestratorpb.CheckState_CHECK_STATE_FINAL:
		cfg.onState = &state
		return nil
	default:
		return fmt.Errorf("attrs: invalid check state: %v", state)
	}
}

// WithCheckOnState sets the CheckState on which the attribute is evaluated.
func WithCheckOnState(state orchestratorpb.CheckState) CheckAttributeArg {
	return checkStateArg(state)
}

type attrTypeArg orchestratorpb.AttributeType

func (a attrTypeArg) apply(cur *orchestratorpb.AttributeType) (*orchestratorpb.AttributeType, error) {
	if cur != nil {
		return nil, fmt.Errorf("attrs: cannot overwrite attribute type %v with %v", *cur, orchestratorpb.AttributeType(a))
	}
	switch orchestratorpb.AttributeType(a) {
	case orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL,
		orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL_LIST,
		orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64,
		orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64_LIST,
		orchestratorpb.AttributeType_ATTRIBUTE_TYPE_STRING,
		orchestratorpb.AttributeType_ATTRIBUTE_TYPE_STRING_LIST:
		t := orchestratorpb.AttributeType(a)
		return &t, nil
	default:
		return nil, fmt.Errorf("attrs: invalid attribute type: %v", orchestratorpb.AttributeType(a))
	}
}

func (a attrTypeArg) applyStage(cfg *stageConfig) error {
	var err error
	cfg.attributeType, err = a.apply(cfg.attributeType)
	return err
}

func (a attrTypeArg) applyCheck(cfg *checkConfig) error {
	var err error
	cfg.attributeType, err = a.apply(cfg.attributeType)
	return err
}

// WithAttributeType sets the expected result AttributeType.
func WithAttributeType(attrType orchestratorpb.AttributeType) AttributeArg {
	return attrTypeArg(attrType)
}

func validateAttributeName(name string) error {
	if !attrNameRegex.MatchString(name) {
		return fmt.Errorf("attrs: invalid attribute name %q: expected dot-separated lower_snake_case with at least one dot (e.g. 'namespace.my_attr')", name)
	}
	for _, prefix := range reservedPrefixes {
		if strings.HasPrefix(name, prefix) {
			return fmt.Errorf("attrs: invalid attribute name %q: uses reserved prefix %q", name, prefix)
		}
	}
	return nil
}

// StageAttribute creates a StageAttributeWrite for a Stage node.
//
// Call like:
//
//		StageAttribute("foo.bar", "1+1",
//	      WithStageOnState(orchestratorpb.StageState_STAGE_STATE_PLANNED),
//	      WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64))
//
//		StageAttribute("foo.baz", "true || false",
//	      WithStageOnState(orchestratorpb.StageState_STAGE_STATE_FINAL),
//	      WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL))
//
// AttributeType and StageState can at most be set once, if defined more than
// once an error will be returned.
//
// If on_state is left undefined it will default to STAGE_STATE_FINAL on the
// server side. If attribute_type is not specified it will be inferred on the
// server side.
func StageAttribute(name, expression string, args ...StageAttributeArg) (*orchestratorpb.WriteNodesRequest_StageAttributeWrite, error) {
	if err := validateAttributeName(name); err != nil {
		return nil, err
	}
	if expression == "" {
		return nil, errors.New("attrs: expression cannot be empty")
	}

	cfg := stageConfig{}
	for _, arg := range args {
		if err := arg.applyStage(&cfg); err != nil {
			return nil, err
		}
	}

	b := orchestratorpb.WriteNodesRequest_StageAttributeWrite_builder{
		Name:          &name,
		Expression:    &expression,
		OnState:       cfg.onState,
		AttributeType: cfg.attributeType,
	}
	return b.Build(), nil
}

// CheckAttribute creates a CheckAttributeWrite for a Check node.
//
// Call like:
//
//		CheckAttribute("foo.bar", "1+1",
//	      WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_PLANNED),
//	      WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_INT64))
//
//		CheckAttribute("foo.baz", "true || false",
//	      WithCheckOnState(orchestratorpb.CheckState_CHECK_STATE_FINAL),
//	      WithAttributeType(orchestratorpb.AttributeType_ATTRIBUTE_TYPE_BOOL))
//
// AttributeType and CheckState can at most be set once, if defined more than
// once an error will be returned.
//
// If on_state is left undefined it will default to CHECK_STATE_FINAL on the
// server side. If attribute_type is not specified it will be inferred on the
// server side.
func CheckAttribute(name, expression string, args ...CheckAttributeArg) (*orchestratorpb.WriteNodesRequest_CheckAttributeWrite, error) {
	if err := validateAttributeName(name); err != nil {
		return nil, err
	}
	if expression == "" {
		return nil, errors.New("attrs: expression cannot be empty")
	}

	cfg := checkConfig{}
	for _, arg := range args {
		if err := arg.applyCheck(&cfg); err != nil {
			return nil, err
		}
	}

	b := orchestratorpb.WriteNodesRequest_CheckAttributeWrite_builder{
		Name:          &name,
		Expression:    &expression,
		OnState:       cfg.onState,
		AttributeType: cfg.attributeType,
	}
	return b.Build(), nil
}

// AddStageAttributes appends attributes to a StageWrite message.
//
// It verifies that all attribute names are unique across existing and incoming
// attributes for the stage.
func AddStageAttributes(sw *orchestratorpb.WriteNodesRequest_StageWrite, attrs ...*orchestratorpb.WriteNodesRequest_StageAttributeWrite) error {
	if sw == nil {
		return errors.New("attrs: stage write cannot be nil")
	}
	seen := make(map[string]struct{}, len(sw.GetAttributes())+len(attrs))
	for _, existing := range sw.GetAttributes() {
		name := existing.GetName()
		if _, ok := seen[name]; ok {
			return fmt.Errorf("attrs: attribute name %q was already present in StageWrite", name)
		}
		seen[name] = struct{}{}
	}
	for _, attr := range attrs {
		name := attr.GetName()
		if err := validateAttributeName(name); err != nil {
			return err
		}
		if _, ok := seen[name]; ok {
			return fmt.Errorf("attrs: duplicate attribute name %q", name)
		}
		seen[name] = struct{}{}
	}
	sw.SetAttributes(append(sw.GetAttributes(), attrs...))
	return nil
}

// AddCheckAttributes appends attributes to a CheckWrite message.
//
// It verifies that all attribute names are unique across existing and incoming
// attributes for the check.
func AddCheckAttributes(cw *orchestratorpb.WriteNodesRequest_CheckWrite, attrs ...*orchestratorpb.WriteNodesRequest_CheckAttributeWrite) error {
	if cw == nil {
		return errors.New("attrs: check write cannot be nil")
	}
	seen := make(map[string]struct{}, len(cw.GetAttributes())+len(attrs))
	for _, existing := range cw.GetAttributes() {
		name := existing.GetName()
		if _, ok := seen[name]; ok {
			return fmt.Errorf("attrs: duplicate attribute name %q", name)
		}
		seen[name] = struct{}{}
	}
	for _, attr := range attrs {
		name := attr.GetName()
		if err := validateAttributeName(name); err != nil {
			return err
		}
		if _, ok := seen[name]; ok {
			return fmt.Errorf("attrs: duplicate attribute name %q", name)
		}
		seen[name] = struct{}{}
	}
	cw.SetAttributes(append(cw.GetAttributes(), attrs...))
	return nil
}
