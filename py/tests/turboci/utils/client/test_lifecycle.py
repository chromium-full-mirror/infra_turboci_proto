# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for lifecycle.py."""

import asyncio
import itertools
import time
import unittest
from unittest import mock

from google.protobuf import any_pb2
from google.protobuf import timestamp_pb2
from google.protobuf import wrappers_pb2
from google.rpc import code_pb2
from turboci.graph.orchestrator.v1 import revision_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2
from turboci.graph.orchestrator.v1 import write_nodes_response_pb2
from turboci.utils import ids
from turboci.utils.client import clients
from turboci.utils.client import errors
from turboci.utils.client import lifecycle
from turboci.utils.client import transports

# pylint: disable=protected-access
# pylint: disable=line-too-long


def make_ts(seconds: int, nanos: int = 0) -> timestamp_pb2.Timestamp:
  return timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)


_state_version_counter = itertools.count(1)


def make_state(
    heartbeat_by_sec: int | None = None,
    cancelled: bool = False,
    state_enum: stage_attempt_state_pb2.StageAttemptState | None = None,
) -> stage_pb2.StageAttemptCurrentState:
  state = stage_pb2.StageAttemptCurrentState()
  state.version.ts.seconds = next(_state_version_counter)
  if heartbeat_by_sec is not None:
    state.heartbeat_by.CopyFrom(make_ts(heartbeat_by_sec))
  if cancelled:
    state.cancelled_at.CopyFrom(revision_pb2.Revision(ts=make_ts(100)))
  if state_enum is not None:
    state.state = state_enum
  return state


def make_stage(
    type_url: str = "type.googleapis.com/test.MyStage",
) -> stage_pb2.Stage:
  stage = stage_pb2.Stage()
  stage.args.type_url = type_url
  return stage


class TestLifecycle(unittest.TestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=transports.TurboCITransport)
    self.client = clients.Sync(
        wpid=self.wpid, transport=self.mock_transport, token="my-token"
    )
    lifecycle._counters.clear()

  def test_re_entry_prevention(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())
    with hb:
      with self.assertRaisesRegex(RuntimeError, "cannot be re-entered"):
        with hb:
          pass

  def test_heartbeats_disabled(self):
    # If no heartbeat_by is returned, we don't start the thread.
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())
    with hb:
      self.assertIsNone(hb._thread)
      self.assertFalse(hb.is_cancelled)

    # Verify transition to RUNNING was sent
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)
    req = self.mock_transport.call_unary.call_args_list[0][0][1]
    self.assertTrue(req.current_attempt.state_transition.HasField("running"))

  def test_happy_path_periodic_heartbeats(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage("type.googleapis.com/happy.Path")
    )

    # Mock calculate_delay to return 0.01s so the thread loops quickly.
    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      with hb:
        time.sleep(0.04)

    self.assertGreaterEqual(self.mock_transport.call_unary.call_count, 3)

    # Verify the first call was RUNNING
    first_req = self.mock_transport.call_unary.call_args_list[0][0][1]
    self.assertTrue(
        first_req.current_attempt.state_transition.HasField("running")
    )
    # Verify simplified UID: prefix + count
    self.assertTrue(
        first_req.current_attempt.state_transition.running.process_uid.endswith(
            "-1"
        )
    )

    # Verify subsequent calls were heartbeats (empty current_attempt)
    for call in self.mock_transport.call_unary.call_args_list[1:-1]:
      req = call[0][1]
      self.assertTrue(req.HasField("current_attempt"))
      self.assertFalse(req.current_attempt.HasField("state_transition"))

  def test_adaptive_delay_and_latency_tracking(self):
    opts = lifecycle.HeartbeatOptions(
        min_buffer_sec=2.0,
        random_factor=0.0,
    )

    state = make_state(100)

    with mock.patch("time.time", return_value=90):
      self.assertEqual(opts.calculate_delay(state), 8.0)

    opts.record_latency(1.0)
    opts.record_latency(2.0)
    opts.record_latency(3.0)
    self.assertEqual(opts.average_latency, 2.0)

    with mock.patch("time.time", return_value=90):
      self.assertEqual(opts.calculate_delay(state), 6.0)

    opts2 = lifecycle.HeartbeatOptions(
        min_buffer_sec=2.0,
        random_factor=0.5,
    )
    with mock.patch("time.time", return_value=90):
      for _ in range(10):
        delay = opts2.calculate_delay(state)
        assert delay
        self.assertTrue(4.0 <= delay <= 8.0, f"delay {delay} out of bounds")

    def mock_write_nodes(*args, **kwargs):
      _ = (args, kwargs)
      if self.mock_transport.call_unary.call_count >= 2:
        return write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10, cancelled=True
            )
        )
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary.side_effect = mock_write_nodes
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())

    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      with hb:
        start = time.time()
        while not hb.is_cancelled and time.time() - start < 1.0:
          time.sleep(0.005)

    self.assertTrue(hb.is_cancelled)

  def test_teardown_and_serialization(self):
    calls = []

    def mock_write_nodes(method, req, options=None):
      _, _ = method, options
      calls.append(req.reason.message)
      time.sleep(0.02)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary.side_effect = mock_write_nodes
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())

    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      with hb:
        time.sleep(0.015)
        hb.start_tearing_down()
        time.sleep(0.02)

    # Verify exact reason messages
    self.assertEqual(calls[0], "starting attempt")
    self.assertIn("tearing_down", calls)

  def test_teardown_cancelled(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10, cancelled=True
            )
        )
    )
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())
    calls = []

    def mock_write_nodes(method, req, options=None):
      _, _ = method, options
      calls.append(req.reason.message)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary.side_effect = mock_write_nodes
    hb.start_tearing_down()

    self.assertEqual(calls[0], "tearing_down[cancelled]")

  def test_teardown_custom_reason_and_details(self):
    captured_reqs = []

    def mock_write_nodes(method, req, options=None):
      _, _ = method, options
      captured_reqs.append(req)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary.side_effect = mock_write_nodes
    hb = lifecycle.execute_stage(client=self.client, stage=make_stage())
    captured_reqs.clear()

    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value="hello"))
    custom_detail = value_write_pb2.ValueWrite(realm="my-realm", data=apb)

    hb.start_tearing_down(
        reason="my-custom-teardown-reason", details=[custom_detail]
    )

    self.assertEqual(len(captured_reqs), 1)
    req = captured_reqs[0]
    self.assertEqual(req.reason.message, "my-custom-teardown-reason")
    self.assertEqual(len(req.reason.details), 1)
    self.assertEqual(req.reason.details[0].realm, "my-realm")

  def test_transient_error_recovery(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(min_delay_sec=0.01)

    transient_error = errors.RetryableRPCError.make("transient")
    default_rsp = write_nodes_response_pb2.WriteNodesResponse(
        current_attempt_state=make_state(int(time.time()) + 10)
    )

    def mock_write_nodes(*args, **kwargs):
      _ = (args, kwargs)
      if self.client.write_nodes.call_count == 2:
        raise transient_error
      return default_rsp

    self.client.write_nodes = mock.Mock(side_effect=mock_write_nodes)
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      with hb:
        # Poll until we see 3 calls
        start = time.time()
        while (
            self.client.write_nodes.call_count < 3 and time.time() - start < 1.0
        ):
          time.sleep(0.001)
        assert hb._thread
        self.assertTrue(hb._thread.is_alive())

    # Verify logging
    mock_logger.warning.assert_called_once()
    self.assertIn(
        "Transient heartbeat failure", mock_logger.warning.call_args[0][0]
    )
    # Verify that cancelled was NOT observed since it recovered
    self.assertFalse(hb.is_cancelled)

  def test_permanent_error_termination(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(min_delay_sec=0.01)

    permanent_error = errors.RPCError.make(
        "permanent", code=code_pb2.PERMISSION_DENIED
    )
    self.client.write_nodes = mock.Mock(
        side_effect=[
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(int(time.time()) + 10)
            ),
            permanent_error,
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(None)
            ),
        ]
    )
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      with hb:
        assert hb._thread
        hb._thread.join(timeout=1.0)
        self.assertFalse(hb._thread.is_alive())

    # Verify logging
    mock_logger.error.assert_called_once()
    self.assertIn(
        "Permanent heartbeat failure", mock_logger.error.call_args[0][0]
    )

  def test_teardown_timeout(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(exit_timeout_sec=0.01)

    # Make the ping block for 50ms, which is longer than the 10ms timeout.
    def mock_write_nodes(*args, **kwargs):
      _, _ = args, kwargs
      time.sleep(0.05)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.client.write_nodes = mock.Mock(side_effect=mock_write_nodes)
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.002):
      with hb:
        # Give the thread a tiny bit of time to start and enter the ping
        time.sleep(0.005)

    # Verify that the timeout warning was logged
    mock_logger.warning.assert_called()
    warning_msgs = [args[0] for args, _ in mock_logger.warning.call_args_list]
    self.assertTrue(any("failed to stop" in msg for msg in warning_msgs))

  def test_ping_timeout_passed(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    opts = lifecycle.HeartbeatOptions(ping_timeout_sec=4.2)
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    with hb:
      pass

    # Verify that CallOptions was passed to call_unary with correct deadline
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)
    call_args = self.mock_transport.call_unary.call_args_list[0]
    options = call_args[0][2]
    self.assertIsNotNone(options)
    self.assertEqual(options.deadline.total_seconds(), 4.2)

  def test_unexpected_error_limit(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(
        min_delay_sec=0.01,
        max_consecutive_unexpected_errors=2,
    )

    # First call (RUNNING) succeeds, subsequent heartbeats raise unexpected
    # errors
    self.client.write_nodes = mock.Mock(
        side_effect=[
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(int(time.time()) + 10)
            ),
            ValueError("unexpected 1"),
            ValueError("unexpected 2"),
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(None)
            ),
        ]
    )
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      with hb:
        assert hb._thread
        hb._thread.join(timeout=1.0)
        self.assertFalse(hb._thread.is_alive())

    # Verify logging
    mock_logger.error.assert_called_once()
    self.assertIn(
        "Too many consecutive unexpected heartbeat failures",
        mock_logger.error.call_args[0][0],
    )

  def test_counter_partitioned_by_type_url(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb1 = lifecycle.execute_stage(
        client=self.client, stage=make_stage("type.A")
    )
    hb2 = lifecycle.execute_stage(
        client=self.client, stage=make_stage("type.B")
    )
    hb3 = lifecycle.execute_stage(
        client=self.client, stage=make_stage("type.A")
    )

    self.assertTrue(hb1.process_uid.endswith("-1"))
    self.assertTrue(hb2.process_uid.endswith("-1"))
    self.assertTrue(hb3.process_uid.endswith("-2"))

  def test_execute_stage_scheduled(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
        transition_to=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_SCHEDULED,
        opts=lifecycle.HeartbeatOptions(transition_on_exit=False),
    )
    with hb:
      pass
    self.assertEqual(self.mock_transport.call_unary.call_count, 1)
    first_req = self.mock_transport.call_unary.call_args[0][1]
    self.assertTrue(
        first_req.current_attempt.state_transition.HasField("scheduled")
    )

  def test_execute_stage_unsupported_state(self):
    with self.assertRaises(ValueError):
      lifecycle.execute_stage(
          client=self.client,
          stage=make_stage(),
          transition_to=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_COMPLETE,
      )

  def test_exit_with_exception_transitions_to_incomplete(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
    )

    with self.assertRaises(ValueError) as ctx:
      with hb:
        raise ValueError("test error")

    self.assertEqual(str(ctx.exception), "test error")

    # 2 calls: RUNNING (execute_stage) and INCOMPLETE (exit)
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)

    second_req = self.mock_transport.call_unary.call_args_list[1][0][1]
    self.assertTrue(
        second_req.current_attempt.state_transition.HasField("incomplete")
    )
    self.assertIn("ValueError: test error", second_req.reason.message)

  def test_exit_with_exception_transition_failure_does_not_mask(self):
    # RUNNING succeeds, but INCOMPLETE fails
    self.mock_transport.call_unary.side_effect = [
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        ),
        errors.RPCError.make("network down"),
    ]
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
    )

    # The original ValueError should still propagate, NOT the RPCError
    with self.assertRaises(ValueError) as ctx:
      with hb:
        raise ValueError("original error")

    self.assertEqual(str(ctx.exception), "original error")
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)

  def test_exit_clean_transitions_to_complete(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    with hb:
      pass

    self.assertEqual(self.mock_transport.call_unary.call_count, 2)
    second_req = self.mock_transport.call_unary.call_args_list[1][0][1]
    self.assertTrue(
        second_req.current_attempt.state_transition.HasField("complete")
    )
    self.assertEqual(second_req.reason.message, "execution_completed")

  def test_exit_clean_already_complete_or_incomplete_does_not_transition(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10,
                state_enum=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_COMPLETE,
            )
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    with hb:
      pass

    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

  def test_exit_with_exception_already_complete_or_incomplete_does_not_transition(
      self,
  ):
    self.mock_transport.call_unary.return_value = write_nodes_response_pb2.WriteNodesResponse(
        current_attempt_state=make_state(
            int(time.time()) + 10,
            state_enum=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_INCOMPLETE,
        )
    )
    hb = lifecycle.execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    with self.assertRaises(ValueError):
      with hb:
        raise ValueError("test error")

    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

  def test_transition_on_exit_disabled(self):
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    opts = lifecycle.HeartbeatOptions(transition_on_exit=False)
    hb = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    with hb:
      pass
    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

    hb2 = lifecycle.execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    with self.assertRaises(ValueError):
      with hb2:
        raise ValueError("test error")
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)


class TestHeartbeatAsync(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=transports.TurboCIAsyncTransport)
    self.client = clients.Async(
        wpid=self.wpid, transport=self.mock_transport, token="my-token"
    )
    lifecycle._counters.clear()

  async def test_re_entry_prevention(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )
    async with hb:
      with self.assertRaisesRegex(RuntimeError, "cannot be re-entered"):
        async with hb:
          pass

  async def test_heartbeats_disabled(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )
    async with hb:
      self.assertIsNone(hb._task)
      self.assertEqual(hb.is_cancelled, False)

  async def test_happy_path_periodic_heartbeats(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage("type.googleapis.com/happy.Path")
    )

    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      async with hb:
        await asyncio.sleep(0.04)

    self.assertGreaterEqual(self.mock_transport.call_unary.call_count, 3)

  async def test_cancellation(self):
    async def mock_write_nodes(*args, **kwargs):
      _ = (args, kwargs)
      if self.mock_transport.call_unary.call_count >= 2:
        return write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10, cancelled=True
            )
        )
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary = mock.AsyncMock(
        side_effect=mock_write_nodes
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )

    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      async with hb:
        async with asyncio.timeout(1.0):
          while not hb.is_cancelled:
            await asyncio.sleep(0.005)

    self.assertTrue(hb.is_cancelled)

  async def test_teardown_and_serialization(self):
    calls = []

    async def mock_write_nodes(method, req, options=None):
      (
          _,
          _,
      ) = (
          method,
          options,
      )
      calls.append(req.reason.message)
      await asyncio.sleep(0.02)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary = mock_write_nodes
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )

    with mock.patch.object(hb.opts, "calculate_delay", return_value=0.01):
      async with hb:
        await asyncio.sleep(0.015)
        await hb.start_tearing_down()
        await asyncio.sleep(0.02)

    self.assertEqual(calls[0], "starting attempt")
    self.assertIn("tearing_down", calls)

  async def test_teardown_cancelled(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10, cancelled=True
            )
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )
    calls = []

    async def mock_write_nodes(method, req, options=None):
      _, _ = method, options
      calls.append(req.reason.message)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(
              int(time.time()) + 10, cancelled=True
          )
      )

    self.mock_transport.call_unary = mock_write_nodes
    await hb.start_tearing_down()

    self.assertEqual(calls[0], "tearing_down[cancelled]")

  async def test_transient_error_recovery(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(min_delay_sec=0.01)

    transient_error = errors.RetryableRPCError.make("transient")
    default_rsp = write_nodes_response_pb2.WriteNodesResponse(
        current_attempt_state=make_state(int(time.time()) + 10)
    )

    async def mock_write_nodes(*args, **kwargs):
      _ = (args, kwargs)
      if self.client.write_nodes.call_count == 2:
        raise transient_error
      return default_rsp

    self.client.write_nodes = mock.AsyncMock(side_effect=mock_write_nodes)
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      async with hb:
        start = asyncio.get_running_loop().time()
        while (
            self.client.write_nodes.call_count < 3
            and asyncio.get_running_loop().time() - start < 1.0
        ):
          await asyncio.sleep(0.001)
        assert hb._task
        self.assertFalse(hb._task.done())

    # Verify logging
    mock_logger.warning.assert_called_once()
    self.assertIn(
        "Transient heartbeat failure", mock_logger.warning.call_args[0][0]
    )
    # Verify that cancelled was NOT observed since it recovered
    self.assertFalse(hb.is_cancelled)

  async def test_permanent_error_termination(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(min_delay_sec=0.01)

    permanent_error = errors.RPCError.make(
        "permanent", code=code_pb2.PERMISSION_DENIED
    )
    self.client.write_nodes = mock.AsyncMock(
        side_effect=[
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(int(time.time()) + 10)
            ),
            permanent_error,
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(None)
            ),
        ]
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      async with hb:
        async with asyncio.timeout(1.0):
          assert hb._task
          await hb._task
        self.assertTrue(hb._task.done())

    # Verify logging
    mock_logger.error.assert_called_once()
    self.assertIn(
        "Permanent heartbeat failure", mock_logger.error.call_args[0][0]
    )

  async def test_teardown_timeout(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(exit_timeout_sec=0.01)

    # Make the ping ignore cancellation and block
    async def mock_write_nodes(*args, **kwargs):
      _, _ = args, kwargs
      try:
        await asyncio.sleep(0.05)
      except asyncio.CancelledError:
        # Non-compliant task: ignore cancellation and block again!
        await asyncio.sleep(0.05)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.client.write_nodes = mock.AsyncMock(side_effect=mock_write_nodes)
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.002):
      async with hb:
        # Give the task a tiny bit of time to start and enter the ping
        await asyncio.sleep(0.005)

    # Verify that the timeout warning was logged
    mock_logger.warning.assert_called()
    warning_msgs = [args[0] for args, _ in mock_logger.warning.call_args_list]
    self.assertTrue(any("failed to stop" in msg for msg in warning_msgs))

  async def test_teardown_custom_reason_and_details(self):
    captured_reqs = []

    async def mock_write_nodes(method, req, options=None):
      _, _ = method, options
      captured_reqs.append(req)
      return write_nodes_response_pb2.WriteNodesResponse(
          current_attempt_state=make_state(int(time.time()) + 10)
      )

    self.mock_transport.call_unary = mock.AsyncMock(
        side_effect=mock_write_nodes
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage()
    )
    captured_reqs.clear()

    apb = any_pb2.Any()
    apb.Pack(wrappers_pb2.StringValue(value="hello"))
    custom_detail = value_write_pb2.ValueWrite(realm="my-realm", data=apb)

    await hb.start_tearing_down(
        reason="my-custom-async-teardown-reason", details=[custom_detail]
    )

    self.assertEqual(len(captured_reqs), 1)
    req = captured_reqs[0]
    self.assertEqual(req.reason.message, "my-custom-async-teardown-reason")
    self.assertEqual(len(req.reason.details), 1)
    self.assertEqual(req.reason.details[0].realm, "my-realm")

  async def test_ping_timeout_passed(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    opts = lifecycle.HeartbeatOptions(ping_timeout_sec=4.2)
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    async with hb:
      pass

    # Verify that CallOptions was passed to call_unary with correct deadline
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)
    call_args = self.mock_transport.call_unary.call_args_list[0]
    options = call_args[0][2]
    self.assertIsNotNone(options)
    self.assertEqual(options.deadline.total_seconds(), 4.2)

  async def test_unexpected_error_limit(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger
    opts = lifecycle.HeartbeatOptions(
        min_delay_sec=0.01,
        max_consecutive_unexpected_errors=2,
    )

    # First call (RUNNING) succeeds, subsequent heartbeats raise unexpected
    # errors
    self.client.write_nodes = mock.AsyncMock(
        side_effect=[
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(int(time.time()) + 10)
            ),
            ValueError("unexpected 1"),
            ValueError("unexpected 2"),
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(None)
            ),
        ]
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )

    with mock.patch.object(opts, "calculate_delay", return_value=0.01):
      async with hb:
        async with asyncio.timeout(1.0):
          assert hb._task
          await hb._task
        self.assertTrue(hb._task.done())

    # Verify logging
    mock_logger.error.assert_called_once()
    self.assertIn(
        "Too many consecutive unexpected heartbeat failures",
        mock_logger.error.call_args[0][0],
    )

  async def test_counter_partitioned_by_type_url(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb1 = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage("type.A")
    )
    hb2 = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage("type.B")
    )
    hb3 = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage("type.A")
    )

    self.assertTrue(hb1.process_uid.endswith("-1"))
    self.assertTrue(hb2.process_uid.endswith("-1"))
    self.assertTrue(hb3.process_uid.endswith("-2"))

  async def test_async_execute_stage_scheduled(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(None)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
        transition_to=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_SCHEDULED,
        opts=lifecycle.HeartbeatOptions(transition_on_exit=False),
    )
    async with hb:
      pass
    self.assertEqual(self.mock_transport.call_unary.call_count, 1)
    first_req = self.mock_transport.call_unary.call_args[0][1]
    self.assertTrue(
        first_req.current_attempt.state_transition.HasField("scheduled")
    )

  async def test_async_execute_stage_unsupported_state(self):
    with self.assertRaises(ValueError):
      await lifecycle.async_execute_stage(
          client=self.client,
          stage=make_stage(),
          transition_to=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_COMPLETE,
      )

  async def test_aexit_with_exception_transitions_to_incomplete(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
    )

    with self.assertRaises(ValueError) as ctx:
      async with hb:
        raise ValueError("test error")

    self.assertEqual(str(ctx.exception), "test error")

    # 2 calls: RUNNING (async_execute_stage) and INCOMPLETE (exit)
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)

    second_req = self.mock_transport.call_unary.call_args_list[1][0][1]
    self.assertTrue(
        second_req.current_attempt.state_transition.HasField("incomplete")
    )
    self.assertIn("ValueError: test error", second_req.reason.message)

  async def test_aexit_with_exception_transition_failure_does_not_mask(self):
    # RUNNING succeeds, but INCOMPLETE fails
    self.mock_transport.call_unary = mock.AsyncMock(
        side_effect=[
            write_nodes_response_pb2.WriteNodesResponse(
                current_attempt_state=make_state(int(time.time()) + 10)
            ),
            errors.RPCError.make("network down"),
        ]
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
    )

    # The original ValueError should still propagate, NOT the RPCError
    with self.assertRaises(ValueError) as ctx:
      async with hb:
        raise ValueError("original error")

    self.assertEqual(str(ctx.exception), "original error")
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)

  async def test_aexit_clean_transitions_to_complete(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    async with hb:
      pass

    self.assertEqual(self.mock_transport.call_unary.call_count, 2)
    second_req = self.mock_transport.call_unary.call_args_list[1][0][1]
    self.assertTrue(
        second_req.current_attempt.state_transition.HasField("complete")
    )
    self.assertEqual(second_req.reason.message, "execution_completed")

  async def test_aexit_clean_already_complete_or_incomplete_does_not_transition(
      self,
  ):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10,
                state_enum=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_COMPLETE,
            )
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    async with hb:
      pass

    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

  async def test_aexit_with_exception_already_complete_or_incomplete_does_not_transition(
      self,
  ):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(
                int(time.time()) + 10,
                state_enum=stage_attempt_state_pb2.STAGE_ATTEMPT_STATE_INCOMPLETE,
            )
        )
    )
    hb = await lifecycle.async_execute_stage(
        client=self.client,
        stage=make_stage(),
    )
    with self.assertRaises(ValueError):
      async with hb:
        raise ValueError("test error")

    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

  async def test_atransition_on_exit_disabled(self):
    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=make_state(int(time.time()) + 10)
        )
    )
    opts = lifecycle.HeartbeatOptions(transition_on_exit=False)
    hb = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    async with hb:
      pass
    self.assertEqual(self.mock_transport.call_unary.call_count, 1)

    hb2 = await lifecycle.async_execute_stage(
        client=self.client, stage=make_stage(), opts=opts
    )
    with self.assertRaises(ValueError):
      async with hb2:
        raise ValueError("test error")
    self.assertEqual(self.mock_transport.call_unary.call_count, 2)


if __name__ == "__main__":
  unittest.main()
