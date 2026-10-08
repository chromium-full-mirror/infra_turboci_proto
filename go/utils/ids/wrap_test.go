// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/testing/protocmp"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func TestWrap(t *testing.T) {
	t.Run("WorkPlan", func(t *testing.T) {
		id := Workplan("wp")
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetWorkPlan(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("Stage", func(t *testing.T) {
		id := Stage("s")
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetStage(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("StageAttempt", func(t *testing.T) {
		id := must(StageAttemptErr(StageNotWorknode, "s", 1))
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetStageAttempt(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("StageEdit", func(t *testing.T) {
		id := must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0)))
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetStageEdit(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("Check", func(t *testing.T) {
		id := Check("c")
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetCheck(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("CheckResult", func(t *testing.T) {
		id := must(CheckResultErr("c", 1))
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetCheckResult(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("CheckEdit", func(t *testing.T) {
		id := must(CheckEditErr("c", time.Unix(1, 0)))
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped.GetCheckEdit(), protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("Identifier", func(t *testing.T) {
		id := Wrap(Check("c"))
		wrapped := Wrap(id)
		if diff := cmp.Diff(id, wrapped, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("nil", func(t *testing.T) {
		var id *idspb.Check
		if got := Wrap(id); got != nil {
			t.Errorf("expected nil, got %v", got)
		}
	})
}

func TestKindOf(t *testing.T) {
	if got, want := KindOf(Workplan("wp")), idspb.IdentifierKind_IDENTIFIER_KIND_WORK_PLAN; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(Stage("s")), idspb.IdentifierKind_IDENTIFIER_KIND_STAGE; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(must(StageAttemptErr(StageNotWorknode, "s", 1))), idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_ATTEMPT; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0)))), idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_EDIT; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(Check("c")), idspb.IdentifierKind_IDENTIFIER_KIND_CHECK; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(must(CheckResultErr("c", 1))), idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_RESULT; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
	if got, want := KindOf(must(CheckEditErr("c", time.Unix(1, 0)))), idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_EDIT; got != want {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestRoot(t *testing.T) {
	t.Run("WorkPlan", func(t *testing.T) {
		id := Workplan("wp")
		wp, check, stage := Root(id)
		if diff := cmp.Diff(id, wp, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
		if check != nil {
			t.Errorf("expected nil check, got %v", check)
		}
		if stage != nil {
			t.Errorf("expected nil stage, got %v", stage)
		}
	})

	t.Run("Stage", func(t *testing.T) {
		id := SetWorkplan(Stage("s"), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if check != nil {
			t.Errorf("expected nil check, got %v", check)
		}
		if got := stage.GetId(); got != "s" {
			t.Errorf("got %q, want \"s\"", got)
		}
	})

	t.Run("StageAttempt", func(t *testing.T) {
		id := SetWorkplan(must(StageAttemptErr(StageNotWorknode, "s", 1)), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if check != nil {
			t.Errorf("expected nil check, got %v", check)
		}
		if got := stage.GetId(); got != "s" {
			t.Errorf("got %q, want \"s\"", got)
		}
	})

	t.Run("StageEdit", func(t *testing.T) {
		id := SetWorkplan(must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0))), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if check != nil {
			t.Errorf("expected nil check, got %v", check)
		}
		if got := stage.GetId(); got != "s" {
			t.Errorf("got %q, want \"s\"", got)
		}
	})

	t.Run("Check", func(t *testing.T) {
		id := SetWorkplan(Check("c"), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if got := check.GetId(); got != "c" {
			t.Errorf("got %q, want \"c\"", got)
		}
		if stage != nil {
			t.Errorf("expected nil stage, got %v", stage)
		}
	})

	t.Run("CheckResult", func(t *testing.T) {
		id := SetWorkplan(must(CheckResultErr("c", 1)), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if got := check.GetId(); got != "c" {
			t.Errorf("got %q, want \"c\"", got)
		}
		if stage != nil {
			t.Errorf("expected nil stage, got %v", stage)
		}
	})

	t.Run("CheckEdit", func(t *testing.T) {
		id := SetWorkplan(must(CheckEditErr("c", time.Unix(1, 0))), "wp")
		wp, check, stage := Root(id)
		if got := wp.GetId(); got != "wp" {
			t.Errorf("got %q, want \"wp\"", got)
		}
		if got := check.GetId(); got != "c" {
			t.Errorf("got %q, want \"c\"", got)
		}
		if stage != nil {
			t.Errorf("expected nil stage, got %v", stage)
		}
	})

	t.Run("nil", func(t *testing.T) {
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
	})
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

	if !SameWorkPlan(c1, c2) {
		t.Errorf("expected SameWorkPlan(c1, c2) to be true")
	}
	if SameWorkPlan(c1, c3) {
		t.Errorf("expected SameWorkPlan(c1, c3) to be false")
	}
	if SameWorkPlan(c1, (*idspb.Check)(nil)) {
		t.Errorf("expected SameWorkPlan(c1, nil) to be false")
	}
}
