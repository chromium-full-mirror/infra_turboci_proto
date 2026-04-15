# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
'Test for value.SimpleDataSource and value.pick_data.'

import unittest

from google.protobuf import empty_pb2
from google.protobuf import wrappers_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.utils import value


class TestAddSetRef(unittest.TestCase):

  def test_set_ref_ok(self):
    refs: list[value_ref_pb2.ValueRef] = []
    value.set_ref(refs, value.ref(empty_pb2.Empty(), 'project:realm'))
    value.set_ref(
        refs, value.ref(wrappers_pb2.StringValue(value='yo'), 'project:realm')
    )
    value.set_ref(
        refs, value.ref(wrappers_pb2.Int64Value(value=100), 'project:realm')
    )
    value.set_ref(
        refs, value.ref(wrappers_pb2.BoolValue(value=True), 'project:realm')
    )

    self.assertListEqual(
        [ref.type_url for ref in refs],
        sorted([
            value.url(wrappers_pb2.BoolValue),
            value.url(empty_pb2.Empty),
            value.url(wrappers_pb2.Int64Value),
            value.url(wrappers_pb2.StringValue),
        ]),
    )

  def test_set_ref_overwrite(self):
    refs: list[value_ref_pb2.ValueRef] = []
    value.set_ref(refs, value.ref(empty_pb2.Empty(), 'project:realm'))
    value.set_ref(
        refs, value.ref(wrappers_pb2.StringValue(value='yo'), 'project:realm')
    )
    value.set_ref(
        refs, value.ref(wrappers_pb2.Int64Value(value=100), 'project:realm')
    )
    value.set_ref(
        refs, value.ref(wrappers_pb2.BoolValue(value=True), 'project:realm')
    )

    # Now overwrite two values.
    value.set_ref(
        refs, value.ref(wrappers_pb2.BoolValue(value=False), 'project:realm')
    )
    value.set_ref(
        refs, value.ref(wrappers_pb2.StringValue(value='no'), 'project:realm')
    )

    self.assertListEqual(
        refs,
        [
            value.ref(wrappers_pb2.BoolValue(value=False), 'project:realm'),
            value.ref(empty_pb2.Empty(), 'project:realm'),
            value.ref(wrappers_pb2.Int64Value(value=100), 'project:realm'),
            value.ref(wrappers_pb2.StringValue(value='no'), 'project:realm'),
        ],
    )

  def test_set_ref_bad_realm(self):
    refs: list[value_ref_pb2.ValueRef] = []
    value.set_ref(refs, value.ref(empty_pb2.Empty(), 'project:realm'))

    with self.assertRaisesRegex(ValueError, 'mismatched realms'):
      value.set_ref(refs, value.ref(empty_pb2.Empty(), 'other-project:realm'))

  def test_add_ref_ok(self):
    refs: list[value_ref_pb2.ValueRef] = []
    value.add_ref(refs, value.ref(empty_pb2.Empty(), 'project:realm'))
    value.add_ref(
        refs, value.ref(wrappers_pb2.StringValue(value='yo'), 'project:realm')
    )
    value.add_ref(
        refs, value.ref(wrappers_pb2.Int64Value(value=100), 'project:realm')
    )
    value.add_ref(
        refs, value.ref(wrappers_pb2.BoolValue(value=True), 'project:realm')
    )

    self.assertListEqual(
        [ref.type_url for ref in refs],
        sorted([
            value.url(wrappers_pb2.BoolValue),
            value.url(empty_pb2.Empty),
            value.url(wrappers_pb2.Int64Value),
            value.url(wrappers_pb2.StringValue),
        ]),
    )

  def test_add_ref_overwrite_fail(self):
    refs: list[value_ref_pb2.ValueRef] = []
    value.set_ref(refs, value.ref(empty_pb2.Empty(), 'project:realm'))

    with self.assertRaisesRegex(ValueError, 'already in refs'):
      value.add_ref(refs, value.ref(empty_pb2.Empty(), 'other-project:realm'))

  def test_find_skips_omitted(self):
    refs: list[value_ref_pb2.ValueRef] = [
        value.ref(wrappers_pb2.BoolValue(value=True), 'project:realm'),
        value.ref(
            wrappers_pb2.StringValue(value='meep'),
            'project:secret-realm',
            omit_reason='OMIT_REASON_NO_ACCESS',
        ),
        value.ref(
            wrappers_pb2.StringValue(value='morp'),
            'project:other-secret-realm',
            omit_reason='OMIT_REASON_NO_ACCESS',
        ),
        value.ref(
            wrappers_pb2.StringValue(value='cool'),
            'project:realm',
        ),
        value.ref(
            wrappers_pb2.StringValue(value='public'),
            'project:public',
        ),
    ]
    _, found_all = value.find_all(refs, value.url(wrappers_pb2.StringValue))
    self.assertEqual(len(found_all), 4)

    found = value.find(refs, value.url(wrappers_pb2.StringValue))
    assert found
    decoded = value.decode({}, found, wrappers_pb2.StringValue)
    self.assertEqual(decoded, wrappers_pb2.StringValue(value='cool'))


if __name__ == '__main__':
  unittest.main()
