// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestPickData(t *testing.T) {
	t.Parallel()

	mkBin := func(val string) *orchestratorpb.ValueData {
		ret := &orchestratorpb.ValueData{}
		ret.SetBinary(&anypb.Any{TypeUrl: "binary", Value: []byte(val)})
		return ret
	}
	mkJson := func(val string) *orchestratorpb.ValueData {
		ret := &orchestratorpb.ValueData{}
		ret.SetJson(orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String("json"),
			Value:   proto.String(val),
		}.Build())
		return ret
	}
	withFail := func(d *orchestratorpb.ValueData, fail orchestratorpb.DataConversionFailure) *orchestratorpb.ValueData {
		ret := proto.Clone(d).(*orchestratorpb.ValueData)
		ret.SetConversionFailure(fail)
		return ret
	}

	t.Run("a is nil", func(t *testing.T) {
		b := mkBin("b")
		ret := PickData(nil, b)
		assert.Equal(t, b, ret)
	})

	t.Run("no-op same", func(t *testing.T) {
		a := mkBin("a")
		ret := PickData(a, a)
		assert.Equal(t, a, ret)
	})

	t.Run("binary + json -> json", func(t *testing.T) {
		a := mkBin("a")
		b := mkJson("b")
		ret := PickData(a, b)
		assert.Equal(t, b, ret)
	})

	t.Run("binary + binary -> no-op", func(t *testing.T) {
		a := mkBin("a")
		b := mkBin("b")
		ret := PickData(a, b)
		assert.Equal(t, a, ret)
	})

	t.Run("json + binary -> no-op", func(t *testing.T) {
		a := mkJson("a")
		b := mkBin("b")
		ret := PickData(a, b)
		assert.Equal(t, a, ret)
	})

	t.Run("json + json -> no-op", func(t *testing.T) {
		a := mkJson("a")
		b := mkJson("b")
		ret := PickData(a, b)
		assert.Equal(t, a, ret)
	})

	t.Run("json + failure -> json", func(t *testing.T) {
		a := mkJson("a")
		b := withFail(mkBin("a"), orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_ERROR)
		ret := PickData(a, b)
		assert.Equal(t, a, ret)
	})

	t.Run("failure merge", func(t *testing.T) {
		a := mkBin("a")
		b := withFail(mkBin("b"), orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_ERROR)
		ret := PickData(a, b)
		// * failure: unset -> set
		assert.Equal(t, b, ret)
	})

	t.Run("existing failure -> no-op", func(t *testing.T) {
		a := withFail(mkBin("a"), orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_ERROR)
		b := withFail(mkBin("b"), orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_NO_DESCRIPTOR)
		ret := PickData(a, b)
		assert.Equal(t, a, ret)
	})

	t.Run("binary w/ failure + json -> json w/o failure", func(t *testing.T) {
		a := withFail(mkBin("a"), orchestratorpb.DataConversionFailure_DATA_CONVERSION_FAILURE_ERROR)
		b := mkJson("b")
		ret := PickData(a, b)
		assert.Equal(t, b, ret)
	})
}
