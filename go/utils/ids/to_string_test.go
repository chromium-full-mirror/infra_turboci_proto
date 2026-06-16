// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package ids

import (
	"fmt"
	"time"
)

var sampleTimeUTC = time.Date(2016, time.February, 3, 4, 5, 6, 7, time.UTC)

func ExampleToString() {
	fmt.Println(ToString(SetWorkplan(Check("my-check"), "my-workplan")))
	fmt.Println(ToString(SetWorkplan(
		must(CheckEditErr("some check", sampleTimeUTC)),
		"the workplan")))
	// Output:
	// Lmy-workplan:Cmy-check
	// Lthe workplan:Csome check:V1454472306/7
}

func ExampleToString_stages() {
	fmt.Println(ToString(SetWorkplan(Stage("my-stage"), "my-workplan")))
	fmt.Println(ToString(SetWorkplan(StageUnknown("my-stage"), "my-workplan")))
	fmt.Println(ToString(SetWorkplan(StageWorkNode("my-stage"), "my-workplan")))
	// Output:
	// Lmy-workplan:Smy-stage
	// Lmy-workplan:?my-stage
	// Lmy-workplan:Nmy-stage
}
