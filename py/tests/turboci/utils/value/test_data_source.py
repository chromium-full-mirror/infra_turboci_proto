# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for value.SimpleDataSource and value.pick_data."""

import unittest

from google.protobuf import any_pb2
from google.protobuf import empty_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.utils import value


class TestSimpleDataSource(unittest.TestCase):

  def test_dict_compatible(self):
    # Make sure that a simple dict is compatible with DataSource.
    src: dict[str, value_data_pb2.ValueData] = {}
    # Use `assertTrue` instead of `assertIsInstance` so typecheckers will
    # squawk if it's incompatible.
    self.assertTrue(isinstance(src, value.DataSource))

  def test_simple_data_source(self):
    sds = value.SimpleDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = value.Digest.compute(apb)
    sds[dgst] = value_data_pb2.ValueData(binary=apb)

    self.assertEqual(sds[dgst], value_data_pb2.ValueData(binary=apb))

    jValueData = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url)
    )
    sds[dgst] = jValueData

    self.assertEqual(sds[dgst], jValueData)

    # This is a merge, so it will still be JSON.
    sds[dgst] = value_data_pb2.ValueData(binary=apb)

    self.assertEqual(sds[dgst], jValueData)

  def test_update(self):
    sds = value.SimpleDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = str(value.Digest.compute(apb))
    sds.update({
        dgst: value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(
                type_url=apb.type_url,
            ),
        ),
    })

    self.assertEqual(sds[dgst].json.type_url, apb.type_url)

    # Updating with a binary value will not change the data.
    sds.update({
        dgst: value_data_pb2.ValueData(binary=apb),
    })
    self.assertEqual(sds[dgst].json.type_url, apb.type_url)

  def test_request_value_data(self):
    sds = value.SimpleDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = str(value.Digest.compute(apb))
    resp = read_workplan_response_pb2.ReadWorkPlanResponse(
        value_data={dgst: value_data_pb2.ValueData(binary=apb)},
    )

    # Use `assertTrue` instead of `assertIsInstance` so typecheckers will
    # squawk if it's incompatible.
    self.assertTrue(isinstance(resp.value_data, value.DataSource))

    sds.update(resp.value_data)

    self.assertEqual(sds[dgst].binary.type_url, apb.type_url)


class TestPickData(unittest.TestCase):

  def test_pick_none(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(None, value_data_pb2.ValueData(binary=apb))

    self.assertEqual(dat, value_data_pb2.ValueData(binary=apb))

  def test_pick_json_to_binary(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(
            binary=apb, conversion_failure='DATA_CONVERSION_FAILURE_ERROR'
        ),
        value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url)
        ),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)
    self.assertFalse(dat.HasField('conversion_failure'))

  def test_pick_binary_to_json(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url)
        ),
        value_data_pb2.ValueData(binary=apb),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)

  def test_pick_failure_to_binary(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(binary=apb),
        value_data_pb2.ValueData(
            binary=apb, conversion_failure='DATA_CONVERSION_FAILURE_ERROR'
        ),
    )
    self.assertEqual(dat.binary.type_url, apb.type_url)
    self.assertEqual(
        dat.conversion_failure,
        value_data_pb2.DataConversionFailure.DATA_CONVERSION_FAILURE_ERROR,
    )

  def test_pick_failure_to_json(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url)
        ),
        value_data_pb2.ValueData(
            conversion_failure='DATA_CONVERSION_FAILURE_ERROR'
        ),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)
    self.assertFalse(dat.HasField('conversion_failure'))


if __name__ == '__main__':
  unittest.main()
