# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for ref, write and ref_from_write."""

import unittest

from google.protobuf import any_pb2
from google.protobuf import wrappers_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2
from turboci.utils import value


class TestUrl(unittest.TestCase):

  def test_type(self):
    self.assertEqual(
        value.url(wrappers_pb2.StringValue),
        'type.googleapis.com/google.protobuf.StringValue',
    )

  def test_instance(self):
    self.assertEqual(
        value.url(wrappers_pb2.StringValue(value='hi')),
        'type.googleapis.com/google.protobuf.StringValue',
    )


class TestRef(unittest.TestCase):

  def test_ok(self):
    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value='morp'))
    self.assertEqual(
        value.write(wrappers_pb2.StringValue(value='morp')),
        value_write_pb2.ValueWrite(
            data=apb,
            realm='$from_container',
        ),
    )

  def test_passthrough(self):
    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value='morp'))

    self.assertEqual(
        value.write(apb),
        value_write_pb2.ValueWrite(
            data=apb,
            realm='$from_container',
        ),
    )


class TestWrite(unittest.TestCase):

  def test_ok(self):
    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value='morp'))
    self.assertEqual(
        value.ref(wrappers_pb2.StringValue(value='morp'), 'some:realm'),
        value_ref_pb2.ValueRef(
            type_url=value.url(wrappers_pb2.StringValue),
            inline=apb,
            digest=str(value.Digest.compute(apb)),
            realm='some:realm',
        ),
    )


if __name__ == '__main__':
  unittest.main()
