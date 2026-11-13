// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"fmt"
)

func ExampleFromString() {
	// A simple workplan ID
	wp, err := FromString("Lmy-workplan")
	if err != nil {
		panic(err)
	}
	fmt.Println(wp.GetWorkPlan().GetId())

	// A check on that workplan
	chk, err := FromString("Lmy-workplan:Cmy-check")
	if err != nil {
		panic(err)
	}
	fmt.Println(chk.GetCheck().GetId())

	// A stage on that workplan
	st, err := FromString("Lmy-workplan:Smy-stage")
	if err != nil {
		panic(err)
	}
	fmt.Println(st.GetStage().GetId())

	// An invalid string
	_, err = FromString("Lmy-workplan:Xwhatever")
	fmt.Println(err)

	// Output:
	// my-workplan
	// my-check
	// my-stage
	// token 1 in "Lmy-workplan:Xwhatever": unexpected key 'X'
}
