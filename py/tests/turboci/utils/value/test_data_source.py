# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for value.SimpleDataSource and value.pick_data."""

import threading
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
    # Typecheckers will verify this assignment.
    _dst: value.DataSource = src

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

    # Typecheckers will verify this assignment.
    _dst: value.DataSource = resp.value_data

    sds.update(resp.value_data)

    self.assertEqual(sds[dgst].binary.type_url, apb.type_url)


  def test_copies_value_data(self):
    """Verifies that SimpleDataSource copies ValueData instead of
    referencing."""
    sds = value.SimpleDataSource()
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = "some_digest"
    val = value_data_pb2.ValueData(binary=apb)
    sds[dgst] = val
    self.assertIsNot(sds[dgst], val)
    self.assertEqual(sds[dgst], val)

    # Test update also copies
    sds2 = value.SimpleDataSource()
    sds2.update({dgst: val})
    self.assertIsNot(sds2[dgst], val)
    self.assertEqual(sds2[dgst], val)


class TestLockedDataSource(unittest.TestCase):

  def test_locked_data_source(self):
    lds = value.LockedDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = "some_digest"

    # Testing setting a new key (might fail with KeyError due to bug)
    lds[dgst] = value_data_pb2.ValueData(binary=apb)

    self.assertEqual(lds[dgst], value_data_pb2.ValueData(binary=apb))

    jValueData = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url)
    )
    lds[dgst] = jValueData

    self.assertEqual(lds[dgst], jValueData)

    # This is a merge, so it will still be JSON.
    lds[dgst] = value_data_pb2.ValueData(binary=apb)

    self.assertEqual(lds[dgst], jValueData)

  def test_update(self):
    lds = value.LockedDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dgst = "some_digest"

    # Testing update with a new key (might fail with KeyError due to bug)
    lds.update({
        dgst: value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(
                type_url=apb.type_url,
            ),
        ),
    })

    self.assertEqual(lds[dgst].json.type_url, apb.type_url)

    # Updating with a binary value will not change the data.
    lds.update({
        dgst: value_data_pb2.ValueData(binary=apb),
    })
    self.assertEqual(lds[dgst].json.type_url, apb.type_url)

  def test_update_deadlock_prevented(self):
    lds1 = value.LockedDataSource()
    lds2 = value.LockedDataSource()

    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())

    lds1["key1"] = value_data_pb2.ValueData(binary=apb)
    lds2["key2"] = value_data_pb2.ValueData(binary=apb)

    errors = []

    def target1():
      try:
        for _ in range(100):
          lds1.update(lds2)
      except Exception as e:
        errors.append(e)

    def target2():
      try:
        for _ in range(100):
          lds2.update(lds1)
      except Exception as e:
        errors.append(e)

    t1 = threading.Thread(target=target1)
    t2 = threading.Thread(target=target2)

    t1.start()
    t2.start()

    # Join with a timeout to avoid hanging the test suite if it deadlocks
    t1.join(timeout=2.0)
    t2.join(timeout=2.0)

    self.assertFalse(t1.is_alive(), "Thread 1 deadlocked!")
    self.assertFalse(t2.is_alive(), "Thread 2 deadlocked!")
    self.assertEqual(errors, [])


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
            binary=apb,
            conversion_failure='DATA_CONVERSION_FAILURE_ERROR'),
        value_data_pb2.ValueData(
            json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url),
        ),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)
    self.assertFalse(dat.HasField('conversion_failure'))

  def test_pick_binary_to_json(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(json=value_data_pb2.ValueData.JsonAny(
            type_url=apb.type_url)),
        value_data_pb2.ValueData(binary=apb),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)

  def test_pick_failure_to_binary(self):
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    dat = value.pick_data(
        value_data_pb2.ValueData(binary=apb),
        value_data_pb2.ValueData(
            binary=apb,
            conversion_failure='DATA_CONVERSION_FAILURE_ERROR'
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
        value_data_pb2.ValueData(json=value_data_pb2.ValueData.JsonAny(
            type_url=apb.type_url)),
        value_data_pb2.ValueData(
            conversion_failure='DATA_CONVERSION_FAILURE_ERROR'
        ),
    )
    self.assertEqual(dat.json.type_url, apb.type_url)
    self.assertFalse(dat.HasField('conversion_failure'))

  def test_pick_data_returns_copy(self):
    # Scenario 1: No existing data, new_data is provided.
    new_data_1 = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(type_url='some_type'))
    result_1 = value.pick_data(None, new_data_1)
    self.assertIsNot(result_1, new_data_1)
    self.assertEqual(result_1, new_data_1)

    # Scenario 2: new_data is chosen over existing_data.
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    existing_data_2 = value_data_pb2.ValueData(binary=apb)
    new_data_2 = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(type_url=apb.type_url))
    result_2 = value.pick_data(existing_data_2, new_data_2)
    self.assertIsNot(result_2, new_data_2)
    self.assertEqual(result_2, new_data_2)


if __name__ == '__main__':
  unittest.main()
