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

  if not ref.HasField('inline') and not ref.HasField('digest'):
    # ref is invalid as it doesn't have either inline or digest set
    return False

  if ref.HasField('inline'):
    if ref.inline != write.data:
      return False

  # TODO: b/505882519 - `digest` will eventually always be set, and
  # `if ref.HasField('digest')` will be redundant. The entirety
  # of this function could be simplified too.
  if ref.HasField('digest'):
    if str(digest.Digest.compute(write.data)) != ref.digest:
      return False

  # If we get here, ref has either inline or digest set and the write matches
  return True


def ref_matches_ref(
    a: value_ref_pb2.ValueRef, b: value_ref_pb2.ValueRef
) -> bool:
  """Returns True if `a` and `b` have the same realm and content."""
  if a.realm != b.realm or a.type_url != b.type_url:
    return False

  a_has_inline, b_has_inline = a.HasField('inline'), b.HasField('inline')
  a_has_digest, b_has_digest = a.HasField('digest'), b.HasField('digest')

  if not a_has_inline and not a_has_digest:
    # ref a is invalid as it doesn't have either inline or digest set
    return False
  if not b_has_inline and not b_has_digest:
    # ref b is invalid as it doesn't have either inline or digest set
    return False

  if a_has_inline and b_has_inline:
    if a.inline != b.inline:
      return False

  # TODO: b/505882519 - `digest` will eventually always be set, and
  # `if a_digest and b_digest` will be redundant. The entirety
  # of this function could be simplified too.
  if a_has_digest and b_has_digest:
    if a.digest != b.digest:
      return False

  # If native comparisons could not be performed for either field,
  # we cross-compute. Since both refs are valid, this only happens
  # if one has only inline and the other has only digest.
  #
  # TODO: b/505882519 - `digest` will eventually always be set,
  # once that is guaranteed these last two checks will become
  # unnecessary; comparing digest vs digest will be sufficient.
  if a_has_inline and b_has_digest:
    if str(digest.Digest.compute(a.inline)) != b.digest:
      return False

  if a_has_digest and b_has_inline:
    if a.digest != str(digest.Digest.compute(b.inline)):
      return False

  return True
