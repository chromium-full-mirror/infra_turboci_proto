# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for value.Digest."""

import hashlib
import unittest

from google.protobuf import any_pb2
from google.protobuf import empty_pb2
from google.protobuf import struct_pb2
from turboci.utils import value


class TestDigest(unittest.TestCase):

  def test_compute(self):
    # These test vectors are copied verbatim from luci-go and should stay
    # in sync.
    cases = [
        (
            "empty",
            empty_pb2.Empty(),
            "zC1HiB0gq_T1muuCh5VIAoC4FjWvxp00E9waqU1YMhkrAQ",
        ),
        (
            "float_val",
            struct_pb2.Value(number_value=123.456),
            "aexUjcBYp_UhSBsbm6TwadrRm0ZAYUrR5mRAKiJ2XtQ2AQ",
        ),
        (
            "long_string",
            struct_pb2.Value(string_value="this is a very long string" * 40000),
            "tvpg39g5kBqzdMKxPOWxvE82_CR13ZmPUmuaq186WyCzvT8B",
        ),
    ]
    for case in cases:
      name, msg, want = case
      with self.subTest(name):
        apb = any_pb2.Any()
        apb.Pack(msg)
        dgst = value.Digest.compute(apb)
        self.assertEqual(str(dgst), want)

        anySerialized = apb.SerializeToString(deterministic=True)
        self.assertEqual(
            value.deterministically_serialize_any(apb), anySerialized
        )

        vd = dgst.to_proto()
        self.assertEqual(vd.size_bytes, apb.ByteSize())
        self.assertEqual(hashlib.sha256(anySerialized).digest(), vd.hash)


if __name__ == "__main__":
  unittest.main()
