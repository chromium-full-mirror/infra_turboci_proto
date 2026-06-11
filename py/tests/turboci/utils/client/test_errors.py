# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for client error translation."""

from __future__ import annotations

import unittest

from google.protobuf import any_pb2
from google.rpc import code_pb2
from google.rpc import status_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.utils.client import errors


class TestErrors(unittest.TestCase):

  def test_basic_error(self):
    err = errors.RPCError("test message")
    self.assertEqual(str(err), "test message")
    self.assertIsNone(err.code)
    self.assertIsNone(err.status)
    self.assertIsNone(err.current_state)
    self.assertIsNone(err.claim_failure)

  def test_non_retryable_error(self):
    # 5 is NOT_FOUND, which is not in the retryable list.
    status = status_pb2.Status(code=5, message="not found")
    err = errors.RPCError.make("failed", status)
    self.assertEqual(str(err), "failed")
    self.assertEqual(err.code, code_pb2.NOT_FOUND)
    self.assertEqual(err.status, status)
    self.assertNotIsInstance(err, errors.RetryableRPCError)

  def test_retryable_error(self):
    # 14 is UNAVAILABLE, which should be retryable.
    status = status_pb2.Status(code=14, message="unavailable")
    err = errors.RPCError.make("failed", status)
    self.assertEqual(str(err), "failed")
    self.assertEqual(err.code, code_pb2.UNAVAILABLE)
    self.assertEqual(err.status, status)
    self.assertIsInstance(err, errors.RetryableRPCError)

  def test_error_with_details(self):
    # Test unpacking of details
    status = status_pb2.Status(code=5, message="failed")

    current_state = stage_pb2.StageAttemptCurrentState(
        state=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_RUNNING,
    )
    claim_failure = stage_pb2.StageAttemptClaimedFailure(
        claimed_by_process_uid="proc-456",
    )

    detail1 = any_pb2.Any()
    detail1.Pack(current_state)
    detail2 = any_pb2.Any()
    detail2.Pack(claim_failure)

    status.details.extend([detail1, detail2])

    err = errors.RPCError.make("failed", status)

    # The message should contain the unpacked details
    self.assertIn("failed", str(err))
    self.assertIn("attempt_state:", str(err))
    self.assertIn("STAGE_ATTEMPT_STATE_RUNNING", str(err))
    self.assertIn("claimed_by: 'proc-456'", str(err))

    self.assertEqual(err.current_state, current_state)
    self.assertEqual(err.claim_failure, claim_failure)


if __name__ == "__main__":
  unittest.main()
