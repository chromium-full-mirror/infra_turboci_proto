# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for TurboCI clients."""

from __future__ import annotations

import unittest
from unittest import mock

from turboci.graph.orchestrator.v1 import read_workplan_request_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
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


if __name__ == '__main__':
  unittest.main()
