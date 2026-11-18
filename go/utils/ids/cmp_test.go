// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"slices"
	"testing"

	"github.com/google/go-cmp/cmp"
	idspb "go.chromium.org/turboci/proto/go/graph/ids/v1"
)

func TestCompare(t *testing.T) {
	generateBunch := func() []*idspb.Identifier {
		return []*idspb.Identifier{
			Wrap(Stage("b")),
			Wrap(Stage("a")),
			Wrap(StageWorkNode("b")),
			Wrap(StageWorkNode("a")),
			Wrap(StageUnknown("b")),
			Wrap(StageUnknown("a")),
			Wrap(Check("b")),
			Wrap(Check("a")),
		}
	}

	setWorkplan := func(plan string, bunch []*idspb.Identifier) []*idspb.Identifier {
		for i, id := range bunch {
			bunch[i] = SetWorkplan(id, plan)
		}
		return bunch
	}

	var ids []*idspb.Identifier
	ids = []*idspb.Identifier{
		Wrap(Workplan("a")),
		Wrap(Workplan("b")),
	}
	ids = append(ids, generateBunch()...)
	ids = append(ids, setWorkplan("b", generateBunch())...)
	ids = append(ids, setWorkplan("a", generateBunch())...)
	ids = append(ids, setWorkplan("aa", generateBunch())...)
	ids = append(ids, setWorkplan("az", generateBunch())...)

	slices.SortFunc(ids, Compare)

	var got []string
	for _, id := range ids {
		got = append(got, ToString(id))
	}

	want := []string{
		":?a",
		":?b",
		":Ca",
		":Cb",
		":Na",
		":Nb",
		":Sa",
		":Sb",
		"La",
		"La:?a",
		"La:?b",
		"La:Ca",
		"La:Cb",
		"La:Na",
		"La:Nb",
		"La:Sa",
		"La:Sb",
		"Laa:?a",
		"Laa:?b",
		"Laa:Ca",
		"Laa:Cb",
		"Laa:Na",
		"Laa:Nb",
		"Laa:Sa",
		"Laa:Sb",
		"Laz:?a",
		"Laz:?b",
		"Laz:Ca",
		"Laz:Cb",
		"Laz:Na",
		"Laz:Nb",
		"Laz:Sa",
		"Laz:Sb",
		"Lb",
		"Lb:?a",
		"Lb:?b",
		"Lb:Ca",
		"Lb:Cb",
		"Lb:Na",
		"Lb:Nb",
		"Lb:Sa",
		"Lb:Sb",
	}
	if diff := cmp.Diff(want, got); diff != "" {
		t.Errorf("Wrong sorted order (-want +got):\n%s", diff)
	}
}
