# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for decode/lookup/find/results."""

import unittest

from google.protobuf import struct_pb2
from google.protobuf import wrappers_pb2
from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.utils import value


class TestDecode(unittest.TestCase):

  def test_inline(self):
    ref = value.ref(wrappers_pb2.StringValue(value='norp'), 'project:realm')
    decoded = value.decode({}, ref, wrappers_pb2.StringValue)
    self.assertEqual(decoded, wrappers_pb2.StringValue(value='norp'))

  def test_externed(self):
    ref = value.ref(wrappers_pb2.StringValue(value='norp'), 'project:realm')
    ds = value.SimpleDataSource()
    value.absorb_inline(ds, ref)

    decoded = value.decode(ds, ref, wrappers_pb2.StringValue)
    self.assertEqual(decoded, wrappers_pb2.StringValue(value='norp'))

  def test_externed_json(self):
    struct = struct_pb2.Struct()
    struct.update({'key': [1, 2, 3]})
    ref = value.ref(struct, 'project:realm')
    ds = value.SimpleDataSource()
    value.absorb_inline(ds, ref)

    ds[ref.digest].json.type_url = ref.type_url
    ds[ref.digest].json.value = r'{"key":[1,2,3]}'

    decoded = value.decode(ds, ref, struct_pb2.Struct)
    want = struct_pb2.Struct()
    want.update({'key': [1, 2, 3]})
    self.assertEqual(decoded, want)

  def test_missing_data(self):
    ref = value_ref_pb2.ValueRef(
        realm='project:realm',
        digest='fake-digest',
        type_url=value.url(wrappers_pb2.StringValue),
    )
    with self.assertRaisesRegex(ValueError, 'could not find data'):
      value.decode({}, ref, wrappers_pb2.StringValue)


class TestLookup(unittest.TestCase):

  def test_ok(self):
    refs: list[value_ref_pb2.ValueRef] = [
        value.ref(wrappers_pb2.BoolValue(value=True), 'project:realm'),
        value.ref(
            wrappers_pb2.StringValue(value='morp'),
            'project:other-secret-realm',
            omit_reason='OMIT_REASON_NO_ACCESS',
        ),
        value.ref(
            wrappers_pb2.StringValue(value='meep'),
            'project:secret-realm',
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

    decoded = value.lookup({}, refs, wrappers_pb2.StringValue)
    self.assertEqual(decoded, wrappers_pb2.StringValue(value='cool'))

  def test_none(self):
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
            wrappers_pb2.StringValue(value='public'),
            'project:public',
        ),
        value.ref(
            wrappers_pb2.StringValue(value='cool'),
            'project:realm',
        ),
    ]

    decoded = value.lookup({}, refs, wrappers_pb2.Int64Value)
    self.assertIsNone(decoded)

    decoded = value.lookup({}, [], wrappers_pb2.Int64Value)
    self.assertIsNone(decoded)


class TestResults(unittest.TestCase):

  def test_ok(self):
    def _mkdat(
        val: int | str | bool, omit: bool = False
    ) -> value_ref_pb2.ValueRef:
      omit_reason = None
      realm = 'project:realm'
      if omit:
        omit_reason = 'OMIT_REASON_NO_ACCESS'
        realm = 'project:secret'

      if isinstance(val, bool):
        return value.ref(
            wrappers_pb2.BoolValue(value=val), realm, omit_reason=omit_reason
        )

      if isinstance(val, int):
        return value.ref(
            wrappers_pb2.Int64Value(value=val), realm, omit_reason=omit_reason
        )

      return value.ref(
          wrappers_pb2.StringValue(value=val), realm, omit_reason=omit_reason
      )

    check = check_pb2.Check(
        results=[
            check_pb2.Check.Result(
                data=sorted(
                    [
                        _mkdat('hi'),
                        _mkdat(100, omit=True),
                    ],
                    key=lambda x: x.type_url,
                ),
            ),
            check_pb2.Check.Result(
                data=sorted(
                    [
                        _mkdat('no', omit=True),
                        _mkdat(200, omit=True),
                        _mkdat(True),
                    ],
                    key=lambda x: x.type_url,
                ),
            ),
            check_pb2.Check.Result(
                data=sorted(
                    [
                        _mkdat('whee'),
                        _mkdat(300),
                        _mkdat(True),
                    ],
                    key=lambda x: x.type_url,
                ),
            ),
        ],
    )

    self.assertEqual(
        value.results({}, check, wrappers_pb2.StringValue),
        [
            wrappers_pb2.StringValue(value='hi'),
            wrappers_pb2.StringValue(value='whee'),
        ],
    )
    self.assertEqual(
        value.results({}, check, wrappers_pb2.Int64Value),
        [
            wrappers_pb2.Int64Value(value=300),
        ],
    )
    self.assertEqual(
        value.results({}, check, wrappers_pb2.BoolValue),
        [
            wrappers_pb2.BoolValue(value=True),
            wrappers_pb2.BoolValue(value=True),
        ],
    )


if __name__ == '__main__':
  unittest.main()
