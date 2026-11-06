# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for ref, write and ref_from_write."""

import unittest

from google.protobuf import any_pb2
from google.protobuf import wrappers_pb2
from testing.tags import demo_pb2
from turboci.graph.orchestrator.v1 import tags_pb2
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

  def test_any_fails(self):
    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value='morp'))

    with self.assertRaisesRegex(ValueError, r'google\.protobuf\.Any'):
      value.write(apb)


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

  def test_tags_are_added(self):
    msg = demo_pb2.MyMessage(tagged_field='hello')
    apb = any_pb2.Any()
    apb.Pack(msg)
    expected_tags = [
        tags_pb2.Tag(
            key='testing.tags.MyMessage.tagged_field',
            values=[
                tags_pb2.Tag.Value(
                    str_value='hello',
                )
            ],
        )
    ]
    self.assertEqual(
        value.write(msg, 'some:realm'),
        value_write_pb2.ValueWrite(
            data=apb,
            realm='some:realm',
            tags=expected_tags,
        ),
    )
    self.assertEqual(
        value.ref(msg, 'some:realm'),
        value_ref_pb2.ValueRef(
            type_url=value.url(demo_pb2.MyMessage),
            inline=apb,
            digest=str(value.Digest.compute(apb)),
            realm='some:realm',
            tags=expected_tags,
        ),
    )


if __name__ == '__main__':
  import sys
  import unittest.util

  if '-v' in sys.argv or '--verbose' in sys.argv:
    unittest.util._MAX_LENGTH = 999999999  # pyrefly: ignore [bad-assignment]
    unittest.TestCase.maxDiff = None
  unittest.main()
