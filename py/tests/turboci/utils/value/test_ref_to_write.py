# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for ref_to_write."""

from __future__ import annotations

import dataclasses
import typing
import unittest

from google.protobuf import descriptor_pool
from google.protobuf import duration_pb2
from google.protobuf import json_format
from google.protobuf import struct_pb2
from turboci.graph.orchestrator.v1 import omit_reason_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2
from turboci.utils import tags
from turboci.utils import value


@dataclasses.dataclass
class _Case:
  name: str
  ref_fn: None | typing.Callable[[value_ref_pb2.ValueRef], None] = None
  want_fn: None | typing.Callable[[value_write_pb2.ValueWrite], None] = None
  want_err: str = ''
  want_omit: None | omit_reason_pb2.OmitReason = None


class TestRefToWrite(unittest.TestCase):

  def test_ref_to_write(self) -> None:
    realm = 'proj:somerealm'

    dat1 = value.write(duration_pb2.Duration(seconds=10), realm)
    msg2 = struct_pb2.Value(string_value='hi')
    dat2 = value.ref(msg2, realm)

    tag_list = tags.Map.make(tags.make('some.tag')).to_proto()

    source = value.SimpleDataSource()
    source[str(value.Digest.compute(dat1.data))] = value_data_pb2.ValueData(
        binary=dat1.data,
    )
    source['badc0ffee'] = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(
            type_url=value.url(struct_pb2.ListValue),
            value='I am a teapot',
        ),
    )
    value.absorb_inline(source, dat2)
    source[dat2.digest] = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(
            type_url=dat2.type_url,
            value=json_format.MessageToJson(msg2),
        ),
    )

    def _inline_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.digest = str(value.Digest.compute(dat1.data))
      ref.inline.CopyFrom(dat1.data)
      ref.tags.extend(tag_list)

    def _outline_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.digest = str(value.Digest.compute(dat1.data))
      ref.tags.extend(tag_list)

    def _want_dat1(vw: value_write_pb2.ValueWrite) -> None:
      vw.MergeFrom(dat1)
      vw.tags.extend(tag_list)

    def _outline_json_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.MergeFrom(dat2)
      ref.tags.extend(tag_list)

    def _want_dat2(vw: value_write_pb2.ValueWrite) -> None:
      vw.MergeFrom(value.write(struct_pb2.Value(string_value='hi'), realm))
      vw.tags.extend(tag_list)

    def _omitted_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.omit_reason = omit_reason_pb2.OMIT_REASON_NO_ACCESS

    def _missing_type_url_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.type_url = value.TYPE_URL_PREFIX + 'potato.Cannon'

    def _corrupt_json_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.type_url = value.url(struct_pb2.ListValue)
      ref.digest = 'badc0ffee'

    def _missing_data_ref(ref: value_ref_pb2.ValueRef) -> None:
      ref.type_url = value.url(struct_pb2.ListValue)
      ref.digest = 'nonexistent'

    cases = [
        _Case(
            name='ok - inline',
            ref_fn=_inline_ref,
            want_fn=_want_dat1,
        ),
        _Case(
            name='ok - outline',
            ref_fn=_outline_ref,
            want_fn=_want_dat1,
        ),
        _Case(
            name='ok - outline JSON',
            ref_fn=_outline_json_ref,
            want_fn=_want_dat2,
        ),
        _Case(
            name='bad - omitted',
            ref_fn=_omitted_ref,
            want_err='data is omitted',
            want_omit=omit_reason_pb2.OMIT_REASON_NO_ACCESS,
        ),
        _Case(
            name='bad - missing type_url',
            ref_fn=_missing_type_url_ref,
            want_err='error getting descriptor',
        ),
        _Case(
            name='bad - corrupt JSON',
            ref_fn=_corrupt_json_ref,
            want_err='error unmarshaling JSON',
        ),
        _Case(
            name='bad - missing data',
            ref_fn=_missing_data_ref,
            want_err='missing data',
        ),
    ]

    for tc in cases:
      with self.subTest(tc.name):
        ref = value_ref_pb2.ValueRef(realm=realm)
        if tc.ref_fn is not None:
          tc.ref_fn(ref)

        if tc.want_err:
          exc_type = (
              value.OmittedDataError
              if tc.want_omit is not None
              else ValueError
          )
          with self.assertRaisesRegex(exc_type, tc.want_err) as ctx:
            value.ref_to_write(source, ref)
          self.assertIsInstance(ctx.exception, ValueError)
          if tc.want_omit is not None:
            assert isinstance(ctx.exception, value.OmittedDataError)
            self.assertEqual(ctx.exception.omit_reason, tc.want_omit)
        else:
          vw = value.ref_to_write(source, ref)
          want = value_write_pb2.ValueWrite()
          if tc.want_fn is not None:
            tc.want_fn(want)
          self.assertEqual(vw, want)

  def test_custom_pool(self) -> None:
    realm = 'proj:somerealm'
    msg = struct_pb2.Value(string_value='hi')
    ref = value.ref(msg, realm)
    source = value.SimpleDataSource()
    value.absorb_inline(source, ref)
    source[ref.digest] = value_data_pb2.ValueData(
        json=value_data_pb2.ValueData.JsonAny(
            type_url=ref.type_url,
            value=json_format.MessageToJson(msg),
        ),
    )

    empty_pool = descriptor_pool.DescriptorPool()
    with self.assertRaisesRegex(ValueError, 'error getting descriptor'):
      value.ref_to_write(source, ref, pool=empty_pool)


if __name__ == '__main__':
  unittest.main()
