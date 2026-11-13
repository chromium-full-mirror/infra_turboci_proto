# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for value.iter."""

from __future__ import annotations

import unittest

from testing.vectors.value.refs_in import test_case_pb2
from tests.turboci.utils.internal import test_vector
from tests.turboci.utils.value.refs_in_test_vectors import _REFS_IN_VECTORS
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2
from turboci.utils import value


class TestIter(unittest.TestCase):

  def test_vectors(self):
    def _check(tc: test_case_pb2.RefsIn) -> None:
      which = tc.input.WhichOneof('object')
      obj = getattr(tc.input, which) if which is not None else None

      if tc.HasField('err'):
        with self.assertRaises(ValueError) as cm:
          list(value.refs_in(obj))
        self.assertIn(tc.err, str(cm.exception))
        return

      got = list(value.refs_in(obj))
      for ctx, ref in got:
        self.assertNotEqual(
            ctx.slot,
            value_slot_pb2.VALUE_SLOT_UNKNOWN,
            f'unexpected VALUE_SLOT_UNKNOWN for ref {ref}',
        )

      want: list[tuple[value.RefContext, value_ref_pb2.ValueRef]] = []
      for out in tc.output.refs:
        ident = out.id if out.HasField('id') else None
        if out.HasField('result_data'):
          rd = out.result_data
          ctx: value.RefContext = value.ResultDataRefContext(
              slot=out.slot,
              id=ident,
              idx=rd.idx,
              actor=rd.actor if rd.HasField('actor') else None,
          )
        else:
          ctx = value.CommonRefContext(
              slot=out.slot,
              id=ident,
          )
        want.append((ctx, out.ref))

      self.assertEqual(got, want)

    test_vector.run(self, _REFS_IN_VECTORS, test_case_pb2.RefsIn, _check)


if __name__ == '__main__':
  unittest.main()
