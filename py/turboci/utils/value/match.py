# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helpers for matching ValueRefs and ValueWrites."""

from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2
from turboci.utils.value import digest


def write_matches_ref(
    write: value_write_pb2.ValueWrite, ref: value_ref_pb2.ValueRef
) -> bool:
  """Returns True if `write` realm and content matches `ref`'s."""
  if write.realm != ref.realm or write.data.type_url != ref.type_url:
    return False
  if ref.HasField('inline'):
    return ref.inline == write.data
  return str(digest.Digest.compute(write.data)) == ref.digest


def ref_matches_ref(
    a: value_ref_pb2.ValueRef, b: value_ref_pb2.ValueRef
) -> bool:
  """Returns True if `a` and `b` have the same realm and content."""
  if a.realm != b.realm or a.type_url != b.type_url:
    return False

  a_inline, b_inline = a.HasField('inline'), b.HasField('inline')
  a_digest, b_digest = a.HasField('digest'), b.HasField('digest')

  if a_inline and b_inline:
    return a.inline == b.inline

  if a_inline and b_digest:
    return str(digest.Digest.compute(a.inline)) == b.digest

  if a_digest and b_inline:
    return a.digest == str(digest.Digest.compute(b.inline))

  if a_digest and b_digest:
    return a.digest == b.digest

  return False
