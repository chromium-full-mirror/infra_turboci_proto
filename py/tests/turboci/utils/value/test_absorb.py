# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for absorb."""

import unittest

from google.protobuf import wrappers_pb2
from turboci.utils import value


class TestAbsorb(unittest.TestCase):

  def test_absorb_inline_clears_inline_field(self):
    ref = value.ref(wrappers_pb2.StringValue(value='norp'), 'project:realm')
    ds = value.SimpleDataSource()

    # Assert initially that the inline field is present
    self.assertTrue(ref.HasField('inline'))

    # Act
    value.absorb_inline(ds, ref)

    # Assert that it has been cleared
    self.assertFalse(ref.HasField('inline'))


if __name__ == '__main__':
  unittest.main()
