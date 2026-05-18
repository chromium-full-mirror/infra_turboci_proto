# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for value.match."""

import unittest

from google.protobuf import timestamp_pb2
from google.protobuf import wrappers_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.utils import value


class TestMatch(unittest.TestCase):

  def test_write_matches_ref(self):
    ds = value.SimpleDataSource()

    msg = wrappers_pb2.StringValue(value='hi')
    write = value.write(msg, realm='project:realm')

    # Match inline
    ref_inline = value.ref(msg, 'project:realm')
    self.assertTrue(value.write_matches_ref(write, ref_inline))

    # Match digest
    ref_digest = value.ref(msg, 'project:realm')
    value.absorb_inline(ds, ref_digest)
    self.assertTrue(value.write_matches_ref(write, ref_digest))

    # Realm mismatch
    ref_realm_mismatch = value.ref(msg, 'other')
    value.absorb_inline(ds, ref_realm_mismatch)
    self.assertFalse(value.write_matches_ref(write, ref_realm_mismatch))

    # Type URL mismatch
    ref_type_mismatch = value.ref(timestamp_pb2.Timestamp(), 'project:realm')
    value.absorb_inline(ds, ref_type_mismatch)
    self.assertFalse(value.write_matches_ref(write, ref_type_mismatch))

    # Content mismatch (inline vs inline)
    ref_content_mismatch_inline = value.ref(
        wrappers_pb2.StringValue(value='other'),
        'project:realm',
    )
    self.assertFalse(
        value.write_matches_ref(write, ref_content_mismatch_inline)
    )

    # Content mismatch (digest)
    ref_content_mismatch_digest = value.ref(msg, 'project:realm')
    value.absorb_inline(ds, ref_content_mismatch_digest)
    ref_content_mismatch_digest.digest = 'other'
    self.assertFalse(
        value.write_matches_ref(write, ref_content_mismatch_digest)
    )

  def test_ref_matches_ref(self):
    ds = value.SimpleDataSource()

    msg = wrappers_pb2.StringValue(value='hi')

    ref_a = value.ref(msg, 'project:realm')
    ref_b = value.ref(msg, 'project:realm')
    value.absorb_inline(ds, ref_b)

    # Inline vs Digest
    self.assertTrue(value.ref_matches_ref(ref_a, ref_b))
    self.assertTrue(value.ref_matches_ref(ref_b, ref_a))

    # Pure Digest (has digest but no inline)
    ref_pure_digest = value.ref(msg, 'project:realm')
    value.absorb_inline(ds, ref_pure_digest)
    ref_pure_digest.ClearField('inline')

    # Inline vs Pure Digest
    self.assertTrue(value.ref_matches_ref(ref_a, ref_pure_digest))
    self.assertTrue(value.ref_matches_ref(ref_pure_digest, ref_a))

    # Pure Digest vs Pure Digest
    self.assertTrue(value.ref_matches_ref(ref_pure_digest, ref_pure_digest))

    # Pure Digest mismatch
    ref_pure_digest_diff = value.ref(
        wrappers_pb2.StringValue(value='different'), 'project:realm'
    )
    value.absorb_inline(ds, ref_pure_digest_diff)
    ref_pure_digest_diff.ClearField('inline')
    self.assertFalse(
        value.ref_matches_ref(ref_pure_digest, ref_pure_digest_diff)
    )

    # Inline vs Pure Digest mismatch
    self.assertFalse(value.ref_matches_ref(ref_a, ref_pure_digest_diff))
    # Pure Digest vs Inline mismatch
    self.assertFalse(value.ref_matches_ref(ref_pure_digest_diff, ref_a))

    # Inline vs Inline
    self.assertTrue(value.ref_matches_ref(ref_a, ref_a))

    # Digest vs Digest
    self.assertTrue(value.ref_matches_ref(ref_b, ref_b))

    # Realm mismatch
    ref_c = value.ref(msg, 'other')
    value.absorb_inline(ds, ref_c)
    self.assertFalse(value.ref_matches_ref(ref_a, ref_c))

    # Type URL mismatch
    ref_d = value.ref(timestamp_pb2.Timestamp(), 'project:realm')
    value.absorb_inline(ds, ref_d)
    self.assertFalse(value.ref_matches_ref(ref_a, ref_d))

    # Content mismatch (inline vs digest)
    ref_e = value.ref(wrappers_pb2.StringValue(value='nop'), 'project:realm')
    self.assertFalse(value.ref_matches_ref(ref_a, ref_e))

  def test_ref_matches_ref_invalid_ref_returns_false(self):
    msg = wrappers_pb2.StringValue(value='hi')
    valid_ref = value.ref(msg, 'project:realm')
    invalid_ref = value_ref_pb2.ValueRef(
        realm='project:realm',
        type_url=valid_ref.type_url,
    )

    self.assertFalse(value.ref_matches_ref(valid_ref, invalid_ref))
    self.assertFalse(value.ref_matches_ref(invalid_ref, valid_ref))
    self.assertFalse(value.ref_matches_ref(invalid_ref, invalid_ref))

  def test_write_matches_ref_invalid_ref_returns_false(self):
    msg = wrappers_pb2.StringValue(value='hi')
    write = value.write(msg, realm='project:realm')

    invalid_ref = value_ref_pb2.ValueRef(
        realm='project:realm',
        type_url=write.data.type_url,
    )
    self.assertFalse(value.write_matches_ref(write, invalid_ref))


if __name__ == '__main__':
  unittest.main()
