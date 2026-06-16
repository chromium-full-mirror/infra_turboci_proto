// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"fmt"
	"testing"
	"time"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
	"go.chromium.org/turboci/proto/go/internal/test/assert"
)

func TestCheckErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		cid, err := CheckErr("hello")
		assert.NoErr(t, err)
		assert.Match(t, idspb.Check_builder{
			Id: proto.String("hello"),
		}.Build(), cid)
	})

	t.Run("bad", func(t *testing.T) {
		_, err := CheckErr("hello:world")
		assert.ErrLike(t, err, `id.Check: id: "hello:world" contains ":"`)
	})
}

func TestCheckResultErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := CheckResultErr("h", 1)
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.CheckResult_builder{
				Check: idspb.Check_builder{Id: proto.String("h")}.Build(),
				Idx:   proto.Int32(1),
			}.Build(),
			id,
		)
	})

	t.Run("bad checkid", func(t *testing.T) {
		_, err := CheckResultErr("h:", 1)
		assert.ErrLike(t, err, `id.CheckResult: id.Check: id: "h:" contains ":"`)
	})

	t.Run("bad idx", func(t *testing.T) {
		_, err := CheckResultErr("h", 0)
		assert.ErrLike(t, err, `id.CheckResult: resultIdx: 0 must be in [1, max(int32)]`)
	})
}

func TestCheckEditErr(t *testing.T) {
	ts := time.Unix(12345, 6789)

	t.Run("ok", func(t *testing.T) {
		id, err := CheckEditErr("h", ts)
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.CheckEdit_builder{
				Check:   idspb.Check_builder{Id: proto.String("h")}.Build(),
				Version: timestamppb.New(ts),
			}.Build(),
			id,
		)
	})

	t.Run("bad checkid", func(t *testing.T) {
		_, err := CheckEditErr("h:", ts)
		assert.ErrLike(t, err, `id.CheckEdit: id.Check: id: "h:" contains ":"`)
	})

	t.Run("bad ts", func(t *testing.T) {
		_, err := CheckEditErr("h", time.Time{})
		assert.ErrLike(t, err, `id.CheckEdit: zero timestamp`)
	})
}

func TestStageErr(t *testing.T) {
	t.Run("ok S", func(t *testing.T) {
		id, err := StageErr(StageNotWorknode, "something")
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(false)}.Build(),
			id,
		)
	})
	t.Run("ok N", func(t *testing.T) {
		id, err := StageErr(StageIsWorknode, "something")
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(true)}.Build(),
			id,
		)
	})

	t.Run("empty prefix", func(t *testing.T) {
		_, err := StageErr(StageIsUnknown, "")
		assert.ErrLike(t, err, `id.Stage: stageID: zero length`)
	})

	t.Run("bad format", func(t *testing.T) {
		_, err := StageErr(StageIsUnknown, "some:thing")
		assert.ErrLike(t, err, `id.Stage: stageID: "some:thing" contains ":"`)
	})
}

func TestStageAttemptErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := StageAttemptErr(StageNotWorknode, "something", 1)
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.StageAttempt_builder{
				Stage: idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(false)}.Build(),
				Idx:   proto.Int32(1),
			}.Build(),
			id,
		)
	})

	t.Run("bad idx", func(t *testing.T) {
		_, err := StageAttemptErr(StageNotWorknode, "something", 0)
		assert.ErrLike(t, err, `id.StageAttempt: attemptIdx: 0 must be in [1, max(int32)]`)
	})
}

func TestStageEditErr(t *testing.T) {
	ts := time.Unix(12345, 6789)

	t.Run("ok", func(t *testing.T) {
		id, err := StageEditErr(StageNotWorknode, "something", ts)
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.StageEdit_builder{
				Stage: idspb.Stage_builder{
					Id:         proto.String("something"),
					IsWorknode: proto.Bool(false),
				}.Build(),
				Version: timestamppb.New(ts),
			}.Build(),
			id,
		)
	})

	t.Run("bad ts", func(t *testing.T) {
		_, err := StageEditErr(StageNotWorknode, "something", time.Time{})
		assert.ErrLike(t, err, `id.StageEdit: zero timestamp`)
	})
}

func TestSetWorkplanErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := CheckErr("c")
		assert.NoErr(t, err)
		id, err = SetWorkplanErr(id, "Lwp")
		assert.NoErr(t, err)
		assert.Match(t,
			idspb.Check_builder{
				WorkPlan: idspb.WorkPlan_builder{Id: proto.String("Lwp")}.Build(),
				Id:       proto.String("c"),
			}.Build(),
			id,
		)
	})

	t.Run("bad workplan", func(t *testing.T) {
		id, err := CheckErr("c")
		assert.NoErr(t, err)
		_, err = SetWorkplanErr(id, "Lw:p")
		assert.ErrLike(t, err, `id.SetWorkplan: workPlanID: "Lw:p" contains ":"`)
	})
}

func TestSetWorkplan(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id := SetWorkplan(must(CheckErr("c")), "Lwp")
		assert.Match(t,
			idspb.Check_builder{
				WorkPlan: idspb.WorkPlan_builder{Id: proto.String("Lwp")}.Build(),
				Id:       proto.String("c"),
			}.Build(),
			id,
		)
	})

	t.Run("panic", func(t *testing.T) {
		assert.PanicLike(t, func() {
			SetWorkplan(must(CheckErr("c")), "Lw:p")
		}, `contains ":"`)
	})
}

func TestStage(t *testing.T) {
	t.Run(`ok`, func(t *testing.T) {
		sid := Stage("hello")
		assert.Match(t, idspb.Stage_builder{
			Id:         proto.String("hello"),
			IsWorknode: proto.Bool(false),
		}.Build(), sid)
	})

	t.Run("panic", func(t *testing.T) {
		assert.PanicLike(t, func() {
			Stage("")
		}, `zero length`)
	})
}

func ExampleSetWorkplan() {
	id := SetWorkplan(Check("my-check"), "my-workplan")
	fmt.Println(ToString(id))
	// Output: Lmy-workplan:Cmy-check
}

func ExampleSetWorkplan_identifier() {
	id := SetWorkplan(Wrap(Check("my-check")), "my-workplan")
	fmt.Println(ToString(id))
	// Output: Lmy-workplan:Cmy-check
}

func ExampleCheck() {
	id := Check("my-check")
	fmt.Println(ToString(id))
	// Output: :Cmy-check
}

func ExampleStage() {
	id := Stage("my-stage")
	fmt.Println(ToString(id))
	// Output: :Smy-stage
}

func ExampleStageUnknown() {
	id := StageUnknown("my-stage")
	fmt.Println(ToString(id))
	// Output: :?my-stage
}

func ExampleStageWorkNode() {
	id := StageWorkNode("my-stage")
	fmt.Println(ToString(id))
	// Output: :Nmy-stage
}

func ExampleWrap() {
	cid := Check("my-check")
	id := Wrap(cid)
	fmt.Printf("%T --> %s\n", cid, ToString(cid))
	fmt.Printf("%T --> %s\n", id, ToString(id))
	// Output:
	// *idspb.Check --> :Cmy-check
	// *idspb.Identifier --> :Cmy-check
}
