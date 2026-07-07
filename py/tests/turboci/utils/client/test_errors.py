# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for client error translation."""

from __future__ import annotations

import unittest

from google.rpc import code_pb2
from google.rpc import status_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import transaction_invariant_pb2
from turboci.utils.client import errors


class TestErrors(unittest.TestCase):

  def test_basic_error(self):
    err = errors.MakeRPCError("test message")
    self.assertEqual(str(err), "test message")
    self.assertIsNone(err.status.code)
    self.assertIsNone(err.status.raw)
    self.assertIsNone(err.status.current_state)
    self.assertIsNone(err.status.claim_failure)
    self.assertIsNone(err.status.conflict)

  def test_non_retryable_error(self):
    status = status_pb2.Status(code=code_pb2.NOT_FOUND, message="not found")
    err = errors.MakeRPCError("failed", status)
    self.assertEqual(str(err), "NOT_FOUND: failed")
    self.assertEqual(err.status.code, code_pb2.NOT_FOUND)
    self.assertEqual(err.status.raw, status)
    self.assertNotIsInstance(err, errors.RetryableRPCError)

  def test_retryable_error(self):
    status = status_pb2.Status(code=code_pb2.UNAVAILABLE, message="unavailable")
    err = errors.MakeRPCError("failed", status)
    self.assertEqual(str(err), "UNAVAILABLE: failed")
    self.assertEqual(err.status.code, code_pb2.UNAVAILABLE)
    self.assertEqual(err.status.raw, status)
    self.assertIsInstance(err, errors.RetryableRPCError)

  def test_claim_error(self):
    status = status_pb2.Status(
        code=code_pb2.FAILED_PRECONDITION, message="claimed"
    )
    status.details.add().Pack(
        stage_pb2.StageAttemptClaimedFailure(claimed_by_process_uid="meep")
    )
    err = errors.MakeRPCError("claimed", status)
    self.assertIn("FAILED_PRECONDITION: claimed", str(err))
    self.assertIn("claimed_by: 'meep'", str(err))
    self.assertEqual(err.status.code, code_pb2.FAILED_PRECONDITION)
    self.assertEqual(err.status.raw, status)
    self.assertIsInstance(err, errors.StageAttemptAlreadyClaimedError)

  def test_error_with_details(self):
    # Test unpacking of details
    status = status_pb2.Status(code=5, message="failed")

    current_state = stage_pb2.StageAttemptCurrentState(
        state=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_RUNNING,
    )
    claim_failure = stage_pb2.StageAttemptClaimedFailure(
        claimed_by_process_uid="proc-456",
    )
    conflict = transaction_invariant_pb2.TransactionConflictFailure()

    status.details.add().Pack(current_state)
    status.details.add().Pack(claim_failure)
    status.details.add().Pack(conflict)

    err = errors.MakeRPCError("failed", status)

    # The message should contain the unpacked details
    self.assertIn("NOT_FOUND: failed", str(err))
    self.assertIn("attempt_state:", str(err))
    self.assertIn("STAGE_ATTEMPT_STATE_RUNNING", str(err))
    self.assertIn("claimed_by: 'proc-456'", str(err))
    self.assertIn("txn conflict: True", str(err))

    self.assertEqual(err.status.current_state, current_state)
    self.assertEqual(err.status.claim_failure, claim_failure)
    self.assertEqual(err.status.conflict, conflict)
    self.assertIsInstance(err, errors.TransactionalPreconditionError)

  def test_makerpcerror_priority(self):
    # If both conflict and claim_failure are present, conflict takes precedence.
    status = status_pb2.Status(code=code_pb2.UNAVAILABLE, message="error")
    status.details.add().Pack(
        stage_pb2.StageAttemptClaimedFailure(claimed_by_process_uid="proc-1")
    )
    err_claim = errors.MakeRPCError("claim test", status)
    self.assertIsInstance(err_claim, errors.StageAttemptAlreadyClaimedError)

    status.details.add().Pack(
        transaction_invariant_pb2.TransactionConflictFailure()
    )
    err_conflict = errors.MakeRPCError("conflict test", status)
    self.assertIsInstance(err_conflict, errors.TransactionalPreconditionError)

  def test_make_helpers(self):
    basic_err = errors.RPCError.make("basic", code=code_pb2.FAILED_PRECONDITION)
    self.assertEqual(basic_err.status.code, code_pb2.FAILED_PRECONDITION)
    self.assertEqual(type(basic_err), errors.RPCError)
    with self.assertRaises(ValueError):
      errors.RPCError.make("should fail", code=code_pb2.UNAVAILABLE)

    retry_err = errors.RetryableRPCError.make(
        "retry", code=code_pb2.UNAVAILABLE
    )
    self.assertEqual(retry_err.status.code, code_pb2.UNAVAILABLE)
    self.assertIsInstance(retry_err, errors.RetryableRPCError)
    with self.assertRaises(ValueError):
      errors.RetryableRPCError.make("should fail", code=code_pb2.NOT_FOUND)

    claim_err = errors.StageAttemptAlreadyClaimedError.make(
        "claimed", claimed_process_uid="proc-x"
    )
    self.assertIsInstance(claim_err, errors.StageAttemptAlreadyClaimedError)
    self.assertEqual(
        claim_err.status.claim_failure.claimed_by_process_uid, "proc-x"
    )

    txn_err = errors.TransactionalPreconditionError.make("conflict")
    self.assertIsInstance(txn_err, errors.TransactionalPreconditionError)
    self.assertIsNotNone(txn_err.status.conflict)


if __name__ == "__main__":
  unittest.main()
