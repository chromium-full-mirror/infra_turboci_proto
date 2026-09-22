// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
	"google.golang.org/protobuf/types/known/timestamppb"

	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func TestCheckErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		cid, err := CheckErr("hello")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.Check_builder{
			Id: proto.String("hello"),
		}.Build()
		if diff := cmp.Diff(want, cid, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad", func(t *testing.T) {
		_, err := CheckErr("hello:world")
		wantErr := `id.Check: id: "hello:world" contains ":"`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestCheckResultErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := CheckResultErr("h", 1)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.CheckResult_builder{
			Check: idspb.Check_builder{Id: proto.String("h")}.Build(),
			Idx:   proto.Int32(1),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad checkid", func(t *testing.T) {
		_, err := CheckResultErr("h:", 1)
		wantErr := `id.CheckResult: id.Check: id: "h:" contains ":"`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})

	t.Run("bad idx", func(t *testing.T) {
		_, err := CheckResultErr("h", 0)
		wantErr := `id.CheckResult: resultIdx: 0 must be in [1, max(int32)]`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestCheckEditErr(t *testing.T) {
	ts := time.Unix(12345, 6789)

	t.Run("ok", func(t *testing.T) {
		id, err := CheckEditErr("h", ts)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.CheckEdit_builder{
			Check:   idspb.Check_builder{Id: proto.String("h")}.Build(),
			Version: timestamppb.New(ts),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad checkid", func(t *testing.T) {
		_, err := CheckEditErr("h:", ts)
		wantErr := `id.CheckEdit: id.Check: id: "h:" contains ":"`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})

	t.Run("bad ts", func(t *testing.T) {
		_, err := CheckEditErr("h", time.Time{})
		wantErr := `id.CheckEdit: zero timestamp`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestStageErr(t *testing.T) {
	t.Run("ok S", func(t *testing.T) {
		id, err := StageErr(StageNotWorknode, "something")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(false)}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})
	t.Run("ok N", func(t *testing.T) {
		id, err := StageErr(StageIsWorknode, "something")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(true)}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("empty prefix", func(t *testing.T) {
		_, err := StageErr(StageIsUnknown, "")
		wantErr := `id.Stage: stageID: zero length`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})

	t.Run("bad format", func(t *testing.T) {
		_, err := StageErr(StageIsUnknown, "some:thing")
		wantErr := `id.Stage: stageID: "some:thing" contains ":"`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestStageAttemptErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := StageAttemptErr(StageNotWorknode, "something", 1)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.StageAttempt_builder{
			Stage: idspb.Stage_builder{Id: proto.String("something"), IsWorknode: proto.Bool(false)}.Build(),
			Idx:   proto.Int32(1),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad idx", func(t *testing.T) {
		_, err := StageAttemptErr(StageNotWorknode, "something", 0)
		wantErr := `id.StageAttempt: attemptIdx: 0 must be in [1, max(int32)]`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestStageEditErr(t *testing.T) {
	ts := time.Unix(12345, 6789)

	t.Run("ok", func(t *testing.T) {
		id, err := StageEditErr(StageNotWorknode, "something", ts)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.StageEdit_builder{
			Stage: idspb.Stage_builder{
				Id:         proto.String("something"),
				IsWorknode: proto.Bool(false),
			}.Build(),
			Version: timestamppb.New(ts),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad ts", func(t *testing.T) {
		_, err := StageEditErr(StageNotWorknode, "something", time.Time{})
		wantErr := `id.StageEdit: zero timestamp`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestSetWorkplanErr(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id, err := CheckErr("c")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		id, err = SetWorkplanErr(id, "Lwp")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		want := idspb.Check_builder{
			WorkPlan: idspb.WorkPlan_builder{Id: proto.String("Lwp")}.Build(),
			Id:       proto.String("c"),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("bad workplan", func(t *testing.T) {
		id, err := CheckErr("c")
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		_, err = SetWorkplanErr(id, "Lw:p")
		wantErr := `id.SetWorkplan: workPlanID: "Lw:p" contains ":"`
		if err == nil || !strings.Contains(err.Error(), wantErr) {
			t.Fatalf("expected error containing %q, got %v", wantErr, err)
		}
	})
}

func TestSetWorkplan(t *testing.T) {
	t.Run("ok", func(t *testing.T) {
		id := SetWorkplan(must(CheckErr("c")), "Lwp")
		want := idspb.Check_builder{
			WorkPlan: idspb.WorkPlan_builder{Id: proto.String("Lwp")}.Build(),
			Id:       proto.String("c"),
		}.Build()
		if diff := cmp.Diff(want, id, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("panic", func(t *testing.T) {
		defer func() {
			r := recover()
			if r == nil || !strings.Contains(fmt.Sprint(r), `contains ":"`) {
				t.Errorf(`expected panic containing "contains \":\"", got: %v`, r)
			}
		}()
		SetWorkplan(must(CheckErr("c")), "Lw:p")
	})
}

func TestStage(t *testing.T) {
	t.Run(`ok`, func(t *testing.T) {
		sid := Stage("hello")
		want := idspb.Stage_builder{
			Id:         proto.String("hello"),
			IsWorknode: proto.Bool(false),
		}.Build()
		if diff := cmp.Diff(want, sid, protocmp.Transform()); diff != "" {
			t.Errorf("mismatch (-want +got):\n%s", diff)
		}
	})

	t.Run("panic", func(t *testing.T) {
		defer func() {
			r := recover()
			if r == nil || !strings.Contains(fmt.Sprint(r), `zero length`) {
				t.Errorf(`expected panic containing "zero length", got: %v`, r)
			}
		}()
		Stage("")
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
