// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"testing"
	"time"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func TestWrap_nil(t *testing.T) {
	var id *idspb.Check
	if got := Wrap(id); got != nil {
		t.Errorf("expected nil, got %v", got)
	}
}

func TestKindOf_nil(t *testing.T) {
	if got, want := KindOf((*idspb.Check)(nil)), idspb.IdentifierKind_IDENTIFIER_KIND_UNKNOWN; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(&idspb.Identifier{}), idspb.IdentifierKind_IDENTIFIER_KIND_UNKNOWN; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestRoot_nil(t *testing.T) {
	wp, check, stage := Root[*idspb.Check](nil)
	if wp != nil {
		t.Errorf("expected nil wp, got %v", wp)
	}
	if check != nil {
		t.Errorf("expected nil check, got %v", check)
	}
	if stage != nil {
		t.Errorf("expected nil stage, got %v", stage)
	}
}

func TestStageRoot(t *testing.T) {
	id := must(StageAttemptErr(StageNotWorknode, "s", 1))
	if got := StageRoot(id).GetId(); got != "s" {
		t.Errorf("got %q, want \"s\"", got)
	}
}

func TestCheckRoot(t *testing.T) {
	id := must(CheckResultErr("c", 1))
	if got := CheckRoot(id).GetId(); got != "c" {
		t.Errorf("got %q, want \"c\"", got)
	}
}

func TestSameRoot(t *testing.T) {
	c1 := Check("c")
	c2, err := CheckEditErr("c", time.Now())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	c3 := Check("other")

	if !SameRoot(c1, c2) {
		t.Errorf("expected SameRoot(c1, c2) to be true")
	}
	if SameRoot(c1, c3) {
		t.Errorf("expected SameRoot(c1, c3) to be false")
	}
	if SameRoot(c1, (*idspb.Check)(nil)) {
		t.Errorf("expected SameRoot(c1, nil) to be false")
	}

	s1 := Stage("s")
	sa, err := StageAttemptErr(StageNotWorknode, "s", 1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	s1wp := SetWorkplan(Stage("s"), "wp")

	if SameRoot(c1, s1) {
		t.Errorf("expected SameRoot(c1, s1) to be false")
	}
	if SameRoot(s1, s1wp) {
		t.Errorf("expected SameRoot(s1, s1wp) to be false")
	}
	if !SameRoot(s1, sa) {
		t.Errorf("expected SameRoot(s1, sa) to be true")
	}

	wp1 := Workplan("wp1")
	wp2 := Workplan("wp2")
	if SameRoot(c1, wp1) {
		t.Errorf("expected SameRoot(c1, wp1) to be false")
	}
	if SameRoot(wp1, c1) {
		t.Errorf("expected SameRoot(wp1, c1) to be false")
	}
	if SameRoot(s1, wp1) {
		t.Errorf("expected SameRoot(s1, wp1) to be false")
	}
	if SameRoot(wp1, s1) {
		t.Errorf("expected SameRoot(wp1, s1) to be false")
	}
	if SameRoot(wp1, wp2) {
		t.Errorf("expected SameRoot(wp1, wp2) to be false")
	}
	if SameRoot(wp1, wp1) {
		t.Errorf("expected SameRoot(wp1, wp1) to be false")
	}
	if SameRoot(c3, sa) {
		t.Errorf("expected SameRoot(c3, sa) to be false")
	}
	if SameRoot(sa, c3) {
		t.Errorf("expected SameRoot(sa, c3) to be false")
	}
}

func TestSameWorkplan(t *testing.T) {
	c1 := SetWorkplan(Check("c1"), "wp")
	c2 := SetWorkplan(Check("c2"), "wp")
	c3 := SetWorkplan(Check("c1"), "other")
	cNoWP1 := Check("c1")
	cNoWP2 := Check("c2")

	if !SameWorkPlan(c1, c2) {
		t.Errorf("expected SameWorkPlan(c1, c2) to be true")
	}
	if SameWorkPlan(c1, c3) {
		t.Errorf("expected SameWorkPlan(c1, c3) to be false")
	}
	if SameWorkPlan(c1, (*idspb.Check)(nil)) {
		t.Errorf("expected SameWorkPlan(c1, nil) to be false")
	}
	if SameWorkPlan(cNoWP1, cNoWP2) {
		t.Errorf("expected SameWorkPlan(cNoWP1, cNoWP2) to be false")
	}
}
