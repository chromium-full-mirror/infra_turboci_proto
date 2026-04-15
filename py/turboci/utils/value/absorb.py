# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helper for writing tests which want to populate DataSource."""

__all__ = [
    'absorb_inline',
]

from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.utils.value import data_source
from turboci.utils.value import digest


def absorb_inline(
    ds: data_source.MutableDataSource, ref: value_ref_pb2.ValueRef
):
  """Consumes the inline data in `ref` into `src`.

  Mutates `ref` to set `digest` in place of `inline`.

  No-op to absorb digest-based refs.
  """
  if ref.HasField('digest'):
    return

  dgst = digest.Digest.compute(ref.inline)
  ds[str(dgst)] = value_data_pb2.ValueData(binary=ref.inline)
  ref.digest = dgst
