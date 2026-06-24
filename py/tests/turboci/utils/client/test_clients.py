# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for TurboCI clients."""

from __future__ import annotations

import unittest
from unittest import mock

from google.protobuf import timestamp_pb2
from turboci.graph.orchestrator.v1 import read_workplan_request_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2
from turboci.graph.orchestrator.v1 import write_nodes_response_pb2
from turboci.utils import client
from turboci.utils import ids


class TestClients(unittest.TestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)

  def test_sync_client_delegation(self):
    mock_transport = mock.Mock(spec=client.TurboCITransport)
    mock_transport.call_unary.return_value = (
        read_workplan_response_pb2.ReadWorkPlanResponse(
            value_data={'digest1': value_data_pb2.ValueData()}
        )
    )

    client_inst = client.Sync(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
    )

    self.assertIsInstance(
        client_inst.read_work_plan(
            read_workplan_request_pb2.ReadWorkPlanRequest()
        ),
        read_workplan_response_pb2.ReadWorkPlanResponse,
    )
    self.assertIn('digest1', client_inst.data)

  @mock.patch('time.sleep')
  def test_sync_client_retry_success(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCITransport)
    retryable_err = client.RetryableRPCError('retryable', None)
    mock_transport.call_unary.side_effect = [
        retryable_err,
        retryable_err,
        read_workplan_response_pb2.ReadWorkPlanResponse(
            value_data={'digest1': value_data_pb2.ValueData()}
        ),
    ]

    mock_logger = mock.Mock()
    client_inst = client.Sync(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
        retry=client.Retry(
            max_retries=3,
            base_delay_sec=1.0,
            backoff_factor=2.0,
            random_factor=0.0,
        ),
    )

    self.assertIsInstance(
        client_inst.read_work_plan(
            read_workplan_request_pb2.ReadWorkPlanRequest()
        ),
        read_workplan_response_pb2.ReadWorkPlanResponse,
    )
    self.assertEqual(mock_transport.call_unary.call_count, 3)
    mock_sleep.assert_has_calls([
        mock.call(1.0),
        mock.call(2.0),
    ])
    self.assertEqual(mock_sleep.call_count, 2)
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            1,
            1.0,
            retryable_err,
        ),
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            2,
            2.0,
            retryable_err,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 2)

  @mock.patch('time.sleep')
  def test_sync_client_retry_failure(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCITransport)
    retryable_err = client.RetryableRPCError('retryable', None)
    mock_transport.call_unary.side_effect = retryable_err

    mock_logger = mock.Mock()
    client_inst = client.Sync(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
        retry=client.Retry(
            max_retries=2,
            base_delay_sec=1.0,
            backoff_factor=2.0,
            random_factor=0.0,
        ),
    )

    with self.assertRaises(client.RetryableRPCError):
      client_inst.read_work_plan(
          read_workplan_request_pb2.ReadWorkPlanRequest()
      )

    self.assertEqual(mock_transport.call_unary.call_count, 3)
    mock_sleep.assert_has_calls([
        mock.call(1.0),
        mock.call(2.0),
    ])
    self.assertEqual(mock_sleep.call_count, 2)
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            1,
            1.0,
            retryable_err,
        ),
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            2,
            2.0,
            retryable_err,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 2)

  @mock.patch('time.sleep')
  def test_sync_client_non_retryable_failure(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCITransport)
    mock_transport.call_unary.side_effect = client.RPCError('fatal', None)

    mock_logger = mock.Mock()
    client_inst = client.Sync(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
    )

    with self.assertRaises(client.RPCError) as ctx:
      client_inst.read_work_plan(
          read_workplan_request_pb2.ReadWorkPlanRequest()
      )

    self.assertNotIsInstance(ctx.exception, client.RetryableRPCError)
    self.assertEqual(mock_transport.call_unary.call_count, 1)
    mock_sleep.assert_not_called()
    mock_logger.warning.assert_not_called()

  def test_sync_client_write_nodes_updates_state(self):
    mock_transport = mock.Mock(spec=client.TurboCITransport)
    mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=stage_pb2.StageAttemptCurrentState(
                version=revision_pb2.Revision(
                    ts=timestamp_pb2.Timestamp(seconds=123)
                )
            )
        )
    )

    client_inst = client.Sync(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
    )
    cb = mock.Mock()
    client_inst.register_on_state_change(cb)

    self.assertIsInstance(
        client_inst.write_nodes(
            write_nodes_request_pb2.WriteNodesRequest()
        ),
        write_nodes_response_pb2.WriteNodesResponse,
    )
    self.assertEqual(client_inst.latest_attempt_state.version.ts.seconds, 123)
    cb.assert_called_once_with(client_inst.latest_attempt_state)


class TestClientsAsync(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)

  async def test_async_client_delegation(self):
    mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    mock_transport.call_unary = mock.AsyncMock(
        return_value=read_workplan_response_pb2.ReadWorkPlanResponse(
            value_data={'digest1': value_data_pb2.ValueData()}
        )
    )

    client_inst = client.Async(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
    )

    self.assertIsInstance(
        await client_inst.read_work_plan(
            read_workplan_request_pb2.ReadWorkPlanRequest()
        ),
        read_workplan_response_pb2.ReadWorkPlanResponse,
    )
    self.assertIn('digest1', client_inst.data)

  @mock.patch('asyncio.sleep')
  async def test_async_client_retry_success(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    retryable_err = client.RetryableRPCError('retryable', None)
    mock_transport.call_unary = mock.AsyncMock(
        side_effect=[
            retryable_err,
            retryable_err,
            read_workplan_response_pb2.ReadWorkPlanResponse(
                value_data={'digest1': value_data_pb2.ValueData()}
            ),
        ]
    )

    mock_logger = mock.Mock()
    client_inst = client.Async(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
        retry=client.Retry(
            max_retries=3,
            base_delay_sec=1.0,
            backoff_factor=2.0,
            random_factor=0.0,
        ),
    )

    self.assertIsInstance(
        await client_inst.read_work_plan(
            read_workplan_request_pb2.ReadWorkPlanRequest()
        ),
        read_workplan_response_pb2.ReadWorkPlanResponse,
    )
    self.assertEqual(mock_transport.call_unary.call_count, 3)
    mock_sleep.assert_has_calls([
        mock.call(1.0),
        mock.call(2.0),
    ])
    self.assertEqual(mock_sleep.call_count, 2)
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            1,
            1.0,
            retryable_err,
        ),
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            2,
            2.0,
            retryable_err,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 2)

  @mock.patch('asyncio.sleep')
  async def test_async_client_retry_failure(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    retryable_err = client.RetryableRPCError('retryable', None)
    mock_transport.call_unary = mock.AsyncMock(side_effect=retryable_err)

    mock_logger = mock.Mock()
    client_inst = client.Async(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
        retry=client.Retry(
            max_retries=2,
            base_delay_sec=1.0,
            backoff_factor=2.0,
            random_factor=0.0,
        ),
    )

    with self.assertRaises(client.RetryableRPCError):
      await client_inst.read_work_plan(
          read_workplan_request_pb2.ReadWorkPlanRequest()
      )

    self.assertEqual(mock_transport.call_unary.call_count, 3)
    mock_sleep.assert_has_calls([
        mock.call(1.0),
        mock.call(2.0),
    ])
    self.assertEqual(mock_sleep.call_count, 2)
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            1,
            1.0,
            retryable_err,
        ),
        mock.call(
            'Transient error in RPC %s, retrying (attempt %d) in %.2fs: %s',
            'ReadWorkPlan',
            2,
            2.0,
            retryable_err,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 2)

  @mock.patch('asyncio.sleep')
  async def test_async_client_non_retryable_failure(self, mock_sleep):
    mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    mock_transport.call_unary = mock.AsyncMock(
        side_effect=client.RPCError('fatal', None)
    )

    mock_logger = mock.Mock()
    client_inst = client.Async(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
        logger=mock_logger,
    )

    with self.assertRaises(client.RPCError) as ctx:
      await client_inst.read_work_plan(
          read_workplan_request_pb2.ReadWorkPlanRequest()
      )

    self.assertNotIsInstance(ctx.exception, client.RetryableRPCError)
    self.assertEqual(mock_transport.call_unary.call_count, 1)
    mock_sleep.assert_not_called()
    mock_logger.warning.assert_not_called()

  async def test_async_client_write_nodes_updates_state(self):
    mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse(
            current_attempt_state=stage_pb2.StageAttemptCurrentState(
                version=revision_pb2.Revision(
                    ts=timestamp_pb2.Timestamp(seconds=456)
                )
            )
        )
    )

    client_inst = client.Async(
        wpid=self.wpid,
        transport=mock_transport,
        token='my-token',
    )
    cb = mock.Mock()
    client_inst.register_on_state_change(cb)

    self.assertIsInstance(
        await client_inst.write_nodes(
            write_nodes_request_pb2.WriteNodesRequest()
        ),
        write_nodes_response_pb2.WriteNodesResponse,
    )
    self.assertEqual(client_inst.latest_attempt_state.version.ts.seconds, 456)
    cb.assert_called_once_with(client_inst.latest_attempt_state)


if __name__ == '__main__':
  unittest.main()
