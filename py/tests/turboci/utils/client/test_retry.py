# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for client retry policy."""

from __future__ import annotations

import unittest

from turboci.utils.client import retry


class TestRetry(unittest.TestCase):

  def test_no_retries(self):
    r = retry.Retry(max_retries=0)
    attempts = list(r.attempts())
    self.assertEqual(attempts, [None])

  def test_with_retries(self):
    r = retry.Retry(
        max_retries=3,
        base_delay_sec=1.0,
        backoff_factor=2.0,
        random_factor=0.0,
    )
    attempts = list(r.attempts())

    # Should yield:
    # 1. 1.0 - sleep time after 1st attempt
    # 2. 2.0 - sleep time after 2nd attempt
    # 3. 4.0 - sleep time after 3rd attempt
    # 4. None - final attempt

    self.assertEqual(len(attempts), 4)
    self.assertEqual(attempts[0], 1.0)
    self.assertEqual(attempts[1], 2.0)
    self.assertEqual(attempts[2], 4.0)
    self.assertEqual(attempts[3], None)

  def test_max_delay(self):
    r = retry.Retry(
        max_retries=3,
        base_delay_sec=2.0,
        backoff_factor=2.0,
        max_delay_sec=3.0,
        random_factor=0.0,
    )
    attempts = list(r.attempts())

    # Delays:
    # 1. 0
    # 2. min(3.0, 2.0 * 2^0) = 2.0
    # 3. min(3.0, 2.0 * 2^1) = 3.0 (capped)
    # 4. min(3.0, 2.0 * 2^2) = 3.0 (capped)

    self.assertEqual(
        attempts,
        [
            2.0,
            3.0,
            3.0,
            None,
        ],
    )

  def test_randomness(self):
    r = retry.Retry(max_retries=1, base_delay_sec=10.0, random_factor=0.5)
    # delay should be between 5.0 and 10.0
    attempts = list(r.attempts())
    self.assertEqual(len(attempts), 2)
    self.assertTrue(5.0 <= attempts[0] <= 10.0)
    self.assertIsNone(attempts[1])


if __name__ == '__main__':
  unittest.main()
