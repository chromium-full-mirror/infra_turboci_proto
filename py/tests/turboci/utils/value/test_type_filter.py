# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for value.type_filter."""

import unittest

from google.protobuf import empty_pb2
from google.protobuf import struct_pb2
from turboci.graph.orchestrator.v1 import type_info_pb2
from turboci.graph.orchestrator.v1 import type_set_pb2
from turboci.utils import value
from turboci.utils.value import type_filter

# pylint: disable=protected-access


class TestTypeSet(unittest.TestCase):

  def test_empty(self):
    ts = type_filter.TypeSet()
    self.assertFalse(ts.matches('hi'))
    self.assertFalse(ts.matches(value.url(empty_pb2.Empty)))

  def test_static(self):
    ts = type_filter.TypeSet([empty_pb2.Empty, struct_pb2.Value])
    self.assertTrue(ts.matches(value.url(empty_pb2.Empty)))
    self.assertTrue(ts.matches(value.url(struct_pb2.Value)))
    self.assertFalse(ts.matches('hi'))
    self.assertFalse(ts.matches(value.url(struct_pb2.ListValue)))

  def test_wildcard_package(self):
    ts = type_filter.TypeSet(['type.googleapis.com/google.protobuf.*'])
    self.assertTrue(ts.matches(value.url(struct_pb2.Value)))
    self.assertTrue(ts.matches(value.url(struct_pb2.ListValue)))
    self.assertTrue(ts.matches(value.url(struct_pb2.Struct)))
    self.assertTrue(ts.matches(value.url(empty_pb2.Empty)))
    self.assertFalse(ts.matches('hi'))
    self.assertFalse(
        ts.matches('type.googleapis.com/other.package.SomeMessage')
    )

  def test_prefix_star(self):
    ts = type_filter.TypeSet([value.TYPE_URL_PREFIX + '*'])
    self.assertTrue(ts.matches(value.url(struct_pb2.Value)))
    self.assertTrue(ts.matches(value.url(empty_pb2.Empty)))
    self.assertFalse(ts.matches('hi'))

  def test_bare_star(self):
    ts = type_filter.TypeSet(['*'])
    self.assertTrue(ts.matches(value.url(struct_pb2.Value)))
    self.assertTrue(ts.matches('hi'))
    self.assertTrue(ts.matches('type.googleapis.com/some.type'))

  def test_bad_prefix(self):
    with self.assertRaises(ValueError):
      type_filter.TypeSet(['asdf*'])

  def test_bad_star(self):
    with self.assertRaises(ValueError):
      type_filter.TypeSet([value.TYPE_URL_PREFIX + 'hello*'])

  def test_double_star(self):
    with self.assertRaises(ValueError):
      type_filter.TypeSet([value.TYPE_URL_PREFIX + '*hello.*'])

  def test_normalized(self):
    ts = type_filter.TypeSet([
        value.TYPE_URL_PREFIX + 'very.long.package.*',
        value.TYPE_URL_PREFIX + 'very.Cool',
        value.TYPE_URL_PREFIX + 'very.long.*',
        value.TYPE_URL_PREFIX + 'very.long.package.Spam',
        value.TYPE_URL_PREFIX + 'very.Cool',
        value.TYPE_URL_PREFIX + 'very.Cool',
    ])
    self.assertEqual(
        ts._patterns,
        [
            value.TYPE_URL_PREFIX + 'very.Cool',
            value.TYPE_URL_PREFIX + 'very.long.*',
        ],
    )

    self.assertTrue(ts.matches(value.TYPE_URL_PREFIX + 'very.long.Cooltype'))
    self.assertTrue(ts.matches(value.TYPE_URL_PREFIX + 'very.Cool'))
    self.assertTrue(
        ts.matches(value.TYPE_URL_PREFIX + 'very.long.package.OtherType')
    )
    self.assertFalse(
        ts.matches(value.TYPE_URL_PREFIX + 'very.longpkg.Cooltype')
    )
    self.assertFalse(ts.matches(value.TYPE_URL_PREFIX + 'very.Notcool'))

  def test_proto_conversion(self):
    pb = type_set_pb2.TypeSet(
        type_urls=[
            value.url(empty_pb2.Empty),
            value.url(struct_pb2.Value),
        ]
    )
    ts = type_filter.TypeSet.from_proto(pb)
    self.assertEqual(ts._patterns, pb.type_urls)

    pb_roundtrip = ts.to_proto()
    self.assertEqual(pb_roundtrip.type_urls, pb.type_urls)


class TestTypeInfo(unittest.TestCase):

  def test_type_info_wants(self):
    # Case 1: not wanted
    ti = type_filter.TypeInfo(
        wanted=type_filter.TypeSet([value.url(empty_pb2.Empty)])
    )
    self.assertIsNone(ti.wants(value.url(struct_pb2.Value)))

    # Case 2: wanted, unknown_jsonpb = False (default) -> BINARY
    self.assertEqual(
        ti.wants(value.url(empty_pb2.Empty)),
        type_filter.TypeInfo.Wanted.BINARY,
    )

    # Case 3: wanted, unknown_jsonpb = True, not known -> JSON
    ti_json = type_filter.TypeInfo(
        wanted=type_filter.TypeSet([value.url(empty_pb2.Empty)]),
        unknown_jsonpb=True,
    )
    self.assertEqual(
        ti_json.wants(value.url(empty_pb2.Empty)),
        type_filter.TypeInfo.Wanted.JSON,
    )

    # Case 4: wanted, unknown_jsonpb = True, known -> BINARY
    ti_known = type_filter.TypeInfo(
        wanted=type_filter.TypeSet([value.url(empty_pb2.Empty)]),
        unknown_jsonpb=True,
        known=type_filter.TypeSet([value.url(empty_pb2.Empty)]),
    )
    self.assertEqual(
        ti_known.wants(value.url(empty_pb2.Empty)),
        type_filter.TypeInfo.Wanted.BINARY,
    )

  def test_type_info_proto_conversion(self):
    pb = type_info_pb2.TypeInfo(
        wanted=type_set_pb2.TypeSet(type_urls=[value.url(empty_pb2.Empty)]),
        unknown_jsonpb=True,
        known=type_set_pb2.TypeSet(type_urls=[value.url(struct_pb2.Value)]),
    )
    ti = type_filter.TypeInfo.from_proto(pb)
    self.assertEqual(ti.wanted._patterns, [value.url(empty_pb2.Empty)])
    self.assertTrue(ti.unknown_jsonpb)
    self.assertEqual(ti.known._patterns, [value.url(struct_pb2.Value)])

    pb_roundtrip = ti.to_proto()
    self.assertEqual(
        pb_roundtrip.wanted.type_urls, [value.url(empty_pb2.Empty)]
    )
    self.assertTrue(pb_roundtrip.unknown_jsonpb)
    self.assertEqual(
        pb_roundtrip.known.type_urls, [value.url(struct_pb2.Value)]
    )


if __name__ == '__main__':
  unittest.main()
