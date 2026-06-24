# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Unified error types and translation helpers for TurboCI Orchestrator."""

from __future__ import annotations

from google.protobuf import json_format
from google.rpc import code_pb2
from google.rpc import status_pb2
from turboci.graph.orchestrator.v1 import stage_pb2

__all__ = [
    'RPCError',
    'RetryableRPCError',
    'StageAttemptNotRunning',
    'TransactionMultipleWritesError',
    'TransactionalPreconditionError',
]


def _is_retryable(code: int) -> bool:
  """Returns True for retriable codes."""
  return code in (
      code_pb2.ABORTED,
      code_pb2.CANCELLED,
      code_pb2.DEADLINE_EXCEEDED,
      code_pb2.INTERNAL,
      code_pb2.RESOURCE_EXHAUSTED,
      code_pb2.UNAVAILABLE,
      code_pb2.UNKNOWN,
  )


class RPCError(Exception):
  """Unified error for Turbo CI Orchestrator Transports.

  Correctly implemented transports must raise this exception.

  Use `RPCError.make` to construct this exception. It will automatically
  return a `RetryableRPCError` subclass if the error is retryable.
  """

  @staticmethod
  def make(
      message: str,
      status: status_pb2.Status | None = None,
  ) -> RPCError:
    """Constructs an RPCError.

    If the status code in the provided status is retryable, this will
    return a RetryableRPCError instance instead.

    Args:
      message: The error message.
      status: The Status message.

    Returns:
      An RPCError or RetryableRPCError instance.
    """
    if status and _is_retryable(status.code):
      return RetryableRPCError(message, status)
    return RPCError(message, status)

  def __init__(
      self,
      message: str,
      status: status_pb2.Status | None = None,
  ):
    current_state: stage_pb2.StageAttemptCurrentState | None = None
    claim_failure: stage_pb2.StageAttemptClaimedFailure | None = None
    code: int | None = None
    if status:
      code = status.code
      for detail in status.details:
        if detail.Is(stage_pb2.StageAttemptCurrentState.DESCRIPTOR):
          current_state = stage_pb2.StageAttemptCurrentState()
          detail.Unpack(current_state)
        elif detail.Is(stage_pb2.StageAttemptClaimedFailure.DESCRIPTOR):
          claim_failure = stage_pb2.StageAttemptClaimedFailure()
          detail.Unpack(claim_failure)
        if current_state and claim_failure:
          break

    msg_parts = [message]
    if current_state:
      cstate = json_format.MessageToJson(current_state, indent=None)
      msg_parts.append(f'  attempt_state: {cstate}')
    if claim_failure:
      msg_parts.append(
          f'  claimed_by: {claim_failure.claimed_by_process_uid!r}'
      )
    super().__init__('\n'.join(msg_parts))
    self.code = code
    self.status = status
    self.current_state = current_state
    self.claim_failure = claim_failure


class RetryableRPCError(RPCError):
  """This is an RPCError which is known to be retriable."""


class TransactionalPreconditionError(Exception):
  """This is raised when the current transaction attempt cannot be completed.

  This will occur on reads when a second read re-observes a node at a newer
  state, or on writes if some of the nodes in the precondition are actually
  at a newer state than what we observed.

  The transaction runner will catch this to start the transaction callback from
  the beginning.
  """


class TransactionMultipleWritesError(Exception):
  """Multiple WriteNodes invocations were used in the same transaction attempt.

  This is not allowed - all writes must be done in a single WriteNodes call
  with the aggregated precondition.

  If you need to do multiple writes, split your transaction into multiple
  pieces, each of them independently observing the necessary precondition for
  that write.
  """


class StageAttemptNotRunning(Exception):
  """Raised from Heartbeater{,Async}.assert_running()."""
