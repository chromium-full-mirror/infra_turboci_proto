// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"testing"
	"time"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestWrap(t *testing.T) {
	t.Run("WorkPlan", func(t *testing.T) {
		id := Workplan("wp")
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetWorkPlan())
	})

	t.Run("Stage", func(t *testing.T) {
		id := Stage("s")
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetStage())
	})

	t.Run("StageAttempt", func(t *testing.T) {
		id := must(StageAttemptErr(StageNotWorknode, "s", 1))
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetStageAttempt())
	})

	t.Run("StageEdit", func(t *testing.T) {
		id := must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0)))
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetStageEdit())
	})

	t.Run("Check", func(t *testing.T) {
		id := Check("c")
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetCheck())
	})

	t.Run("CheckResult", func(t *testing.T) {
		id := must(CheckResultErr("c", 1))
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetCheckResult())
	})

	t.Run("CheckEdit", func(t *testing.T) {
		id := must(CheckEditErr("c", time.Unix(1, 0)))
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped.GetCheckEdit())
	})

	t.Run("Identifier", func(t *testing.T) {
		id := Wrap(Check("c"))
		wrapped := Wrap(id)
		assert.Match(t, id, wrapped)
	})

	t.Run("nil", func(t *testing.T) {
		var id *idspb.Check
		assert.Nil(t, Wrap(id))
	})
}

func TestKindOf(t *testing.T) {
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_WORK_PLAN, KindOf(Workplan("wp")))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_STAGE, KindOf(Stage("s")))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_ATTEMPT, KindOf(must(StageAttemptErr(StageNotWorknode, "s", 1))))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_STAGE_EDIT, KindOf(must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0)))))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_CHECK, KindOf(Check("c")))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_RESULT, KindOf(must(CheckResultErr("c", 1))))
	assert.Equal(t, idspb.IdentifierKind_IDENTIFIER_KIND_CHECK_EDIT, KindOf(must(CheckEditErr("c", time.Unix(1, 0)))))
}

func TestRoot(t *testing.T) {
	t.Run("WorkPlan", func(t *testing.T) {
		id := Workplan("wp")
		wp, check, stage := Root(id)
		assert.Match(t, id, wp)
		assert.Nil(t, check)
		assert.Nil(t, stage)
	})

	t.Run("Stage", func(t *testing.T) {
		id := SetWorkplan(Stage("s"), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Nil(t, check)
		assert.Equal(t, "s", stage.GetId())
	})

	t.Run("StageAttempt", func(t *testing.T) {
		id := SetWorkplan(must(StageAttemptErr(StageNotWorknode, "s", 1)), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Nil(t, check)
		assert.Equal(t, "s", stage.GetId())
	})

	t.Run("StageEdit", func(t *testing.T) {
		id := SetWorkplan(must(StageEditErr(StageNotWorknode, "s", time.Unix(1, 0))), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Nil(t, check)
		assert.Equal(t, "s", stage.GetId())
	})

	t.Run("Check", func(t *testing.T) {
		id := SetWorkplan(Check("c"), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Equal(t, "c", check.GetId())
		assert.Nil(t, stage)
	})

	t.Run("CheckResult", func(t *testing.T) {
		id := SetWorkplan(must(CheckResultErr("c", 1)), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Equal(t, "c", check.GetId())
		assert.Nil(t, stage)
	})

	t.Run("CheckEdit", func(t *testing.T) {
		id := SetWorkplan(must(CheckEditErr("c", time.Unix(1, 0))), "wp")
		wp, check, stage := Root(id)
		assert.Equal(t, "wp", wp.GetId())
		assert.Equal(t, "c", check.GetId())
		assert.Nil(t, stage)
	})

	t.Run("nil", func(t *testing.T) {
		wp, check, stage := Root[*idspb.Check](nil)
		assert.Nil(t, wp)
		assert.Nil(t, check)
		assert.Nil(t, stage)
	})
}

func TestStageRoot(t *testing.T) {
	id := must(StageAttemptErr(StageNotWorknode, "s", 1))
	assert.Equal(t, "s", StageRoot(id).GetId())
}

func TestCheckRoot(t *testing.T) {
	id := must(CheckResultErr("c", 1))
	assert.Equal(t, "c", CheckRoot(id).GetId())
}

func TestSameRoot(t *testing.T) {
	c1 := Check("c")
	c2, err := CheckEditErr("c", time.Now())
	assert.NoErr(t, err)

	c3 := Check("other")

	assert.True(t, SameRoot(c1, c2))
	assert.False(t, SameRoot(c1, c3))
	assert.False(t, SameRoot(c1, (*idspb.Check)(nil)))

	s1 := Stage("s")
	sa, err := StageAttemptErr(StageNotWorknode, "s", 1)
	assert.NoErr(t, err)

	s1wp := SetWorkplan(Stage("s"), "wp")

	assert.False(t, SameRoot(c1, s1))
	assert.False(t, SameRoot(s1, s1wp))
	assert.True(t, SameRoot(s1, sa))
}

func TestSameWorkplan(t *testing.T) {
	c1 := SetWorkplan(Check("c1"), "wp")
	c2 := SetWorkplan(Check("c2"), "wp")
	c3 := SetWorkplan(Check("c1"), "other")

	assert.True(t, SameWorkPlan(c1, c2))
	assert.False(t, SameWorkPlan(c1, c3))
	assert.False(t, SameWorkPlan(c1, (*idspb.Check)(nil)))
}
