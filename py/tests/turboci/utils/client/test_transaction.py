# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for transaction helpers."""

from __future__ import annotations

import unittest
from unittest import mock

from google.protobuf import timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import query_nodes_request_pb2
from turboci.graph.orchestrator.v1 import query_nodes_response_pb2
from turboci.graph.orchestrator.v1 import read_workplan_request_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2
from turboci.graph.orchestrator.v1 import write_nodes_response_pb2
from turboci.utils import client
from turboci.utils import ids
from turboci.utils import value
from turboci.utils.client import transaction

# pylint: disable=protected-access


def make_ts(seconds: int, nanos: int = 0) -> timestamp_pb2.Timestamp:
  return timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)


def make_rev(seconds: int, nanos: int = 0) -> revision_pb2.Revision:
  return revision_pb2.Revision(ts=make_ts(seconds, nanos))


def make_wp(
    wpid: identifier_pb2.WorkPlan, rev_seconds: int
) -> workplan_pb2.WorkPlan:
  return workplan_pb2.WorkPlan(
      identifier=wpid,
      version=make_rev(rev_seconds),
  )


def make_check(
    wpid: identifier_pb2.WorkPlan, check_id: str, rev_seconds: int
) -> check_pb2.Check:
  return check_pb2.Check(
      identifier=ids.check(check_id, wpid),
      version=make_rev(rev_seconds),
  )


def make_stage(
    wpid: identifier_pb2.WorkPlan,
    stage_id: str,
    rev_seconds: int,
    is_worknode: bool = False,
) -> stage_pb2.Stage:
  return stage_pb2.Stage(
      identifier=ids.stage(stage_id, wpid, is_worknode=is_worknode),
      version=make_rev(rev_seconds),
  )


class TestObservedNodeSet(unittest.TestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.other_wpid = ids.workplan(67890)
    self.ns = transaction.ObservedNodeSet(wpid=self.wpid)

  def test_assert_missing_nodes(self):
    self.ns.assert_missing_nodes(
        ids.check('check1', self.wpid),
        ids.stage('stage1', self.wpid),
    )

    self.assertIn(ids.to_string(ids.check('check1')), self.ns.nodes)
    self.assertIn(ids.to_string(ids.stage('stage1')), self.ns.nodes)
    self.assertEqual(len(self.ns.nodes), 2)

  def test_assert_missing_nodes_after_rev_set_raises(self):
    self.ns.observe_ReadWorkPlan(
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    with self.assertRaisesRegex(
        ValueError, 'cannot assert_missing_nodes after doing read/query'
    ):
      self.ns.assert_missing_nodes(ids.check('check1', self.wpid))

  def test_observe_workplan_first_time(self):
    wp = make_wp(self.wpid, 100)
    wp.checks.append(make_check(self.wpid, 'check1', 50))
    wp.stages.append(make_stage(self.wpid, 'stage1', 80))

    self.ns._observe_workplan(wp)

    self.assertEqual(self.ns._rev, wp.version)
    self.assertIn(ids.to_string(ids.check('check1')), self.ns.nodes)
    self.assertIn(ids.to_string(ids.stage('stage1')), self.ns.nodes)

  def test_observe_workplan_after_assert_missing_nodes_raises(self):
    self.ns.assert_missing_nodes(ids.check('check1', self.wpid))

    wp = make_wp(self.wpid, 100)
    with self.assertRaisesRegex(
        ValueError, 'cannot read/query after `assert_missing_nodes`'
    ):
      self.ns._observe_workplan(wp)

  def test_observe_workplan_subsequent_same_or_older_rev(self):
    self.ns._observe_workplan(make_wp(self.wpid, 100))

    wp2 = make_wp(self.wpid, 100)
    wp2.checks.append(make_check(self.wpid, 'check1', 100))
    self.ns._observe_workplan(wp2)

    wp3 = make_wp(self.wpid, 100)
    wp3.stages.append(make_stage(self.wpid, 'stage1', 50))
    self.ns._observe_workplan(wp3)

  def test_observe_workplan_subsequent_newer_rev_raises(self):
    self.ns._observe_workplan(make_wp(self.wpid, 100))

    wp2 = make_wp(self.wpid, 101)
    wp2.checks.append(make_check(self.wpid, 'check1', 101))

    with self.assertRaises(client.RPCError):
      self.ns._observe_workplan(wp2)

  def test_observe_workplan_with_stage_attempts(self):
    wp = make_wp(self.wpid, 100)
    stage = make_stage(self.wpid, 'stage1', 80)

    attempt1 = stage.attempts.add()
    attempt1.identifier.CopyFrom(ids.stage_attempt(1, stage.identifier))
    attempt1.version.CopyFrom(make_rev(70))

    attempt2 = stage.attempts.add()
    attempt2.identifier.CopyFrom(ids.stage_attempt(2, stage.identifier))

    wp.stages.append(stage)

    self.ns._observe_workplan(wp)

    self.assertEqual(self.ns._rev, wp.version)
    self.assertIn(ids.to_string(ids.stage('stage1')), self.ns.nodes)
    self.assertIn(
        ids.to_string(ids.stage_attempt(1, ids.stage('stage1'))), self.ns.nodes
    )
    self.assertNotIn(
        ids.to_string(ids.stage_attempt(2, ids.stage('stage1'))), self.ns.nodes
    )

  def test_observe_workplan_stage_attempt_newer_rev_raises(self):
    self.ns._observe_workplan(make_wp(self.wpid, 100))

    wp2 = make_wp(self.wpid, 100)
    stage = make_stage(self.wpid, 'stage1', 80)
    attempt = stage.attempts.add()
    attempt.identifier.CopyFrom(ids.stage_attempt(1, stage.identifier))
    attempt.version.CopyFrom(make_rev(101))
    wp2.stages.append(stage)

    with self.assertRaises(client.RPCError):
      self.ns._observe_workplan(wp2)

  def test_observe_different_workplan_raises(self):
    with self.assertRaisesRegex(
        ValueError, 'transaction observed multiple workplans'
    ):
      self.ns._observe(ids.check('check1', self.other_wpid))

  def test_observe_read_work_plan(self):
    rsp = read_workplan_response_pb2.ReadWorkPlanResponse(
        workplan=make_wp(self.wpid, 100)
    )
    rsp.workplan.checks.append(make_check(self.wpid, 'check1', 50))

    self.ns.observe_ReadWorkPlan(rsp)

    self.assertEqual(self.ns._rev, rsp.workplan.version)
    self.assertIn(ids.to_string(ids.check('check1')), self.ns.nodes)

  def test_observe_query_nodes(self):
    req = query_nodes_request_pb2.QueryNodesRequest()
    q = req.query.add()
    q.nodes_by_id.nodes.add().check.CopyFrom(ids.check('check1', self.wpid))

    rsp = query_nodes_response_pb2.QueryNodesResponse()
    wp = rsp.workplans.add()
    wp.CopyFrom(make_wp(self.wpid, 100))
    wp.checks.append(make_check(self.wpid, 'check1', 50))
    wp.stages.append(make_stage(self.wpid, 'stage1', 80))

    self.ns.observe_QueryNodes(req, rsp)

    self.assertEqual(self.ns._rev, wp.version)
    self.assertIn(ids.to_string(ids.check('check1')), self.ns.nodes)
    self.assertIn(ids.to_string(ids.stage('stage1')), self.ns.nodes)

  def test_generate_precondition(self):
    self.ns.observe_ReadWorkPlan(
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    self.ns._observe(ids.check('check1', self.wpid))
    self.ns._observe(ids.stage('stage1', self.wpid))

    txn = self.ns.generate_precondition()

    self.assertEqual(txn.snapshot_version, make_rev(100))
    self.assertEqual(len(txn.nodes_observed), 2)
    self.assertEqual(txn.nodes_observed[0].check.work_plan.id, '')
    self.assertEqual(txn.nodes_observed[0].check.id, 'check1')
    self.assertEqual(txn.nodes_observed[1].stage.work_plan.id, '')
    self.assertEqual(txn.nodes_observed[1].stage.id, 'stage1')


class TestApplyNodePredicate(unittest.TestCase):

  def test_apply_node_predicate(self):
    wpid = ids.workplan(12345)
    wp = make_wp(wpid, 100)

    # Check 1: kept, references digest1
    c1 = make_check(wpid, 'check1', 50)
    c1.options.add(digest='digest1')
    wp.checks.append(c1)

    # Check 2: removed, references digest2
    c2 = make_check(wpid, 'check2', 50)
    c2.options.add(digest='digest2')
    wp.checks.append(c2)

    # Stage 1: kept, references digest3
    s1 = make_stage(wpid, 'stage1', 80)
    s1.args.digest = 'digest3'
    wp.stages.append(s1)

    # Stage 2: removed, references digest4
    s2 = make_stage(wpid, 'stage2', 80)
    s2.args.digest = 'digest4'
    wp.stages.append(s2)

    # Populate data source
    data = value.LockedDataSource()
    vdata = value_data_pb2.ValueData()
    data['digest1'] = vdata
    data['digest2'] = vdata
    data['digest3'] = vdata
    data['digest4'] = vdata

    # Predicate: keep 'check1' and 'stage1'
    transaction.apply_node_predicate(
        lambda _, node: node.identifier.id in ('check1', 'stage1'),
        wp,
        data,
    )

    # Verify workplan modifications
    self.assertEqual(len(wp.checks), 1)
    self.assertEqual(wp.checks[0].identifier.id, 'check1')
    self.assertEqual(len(wp.stages), 1)
    self.assertEqual(wp.stages[0].identifier.id, 'stage1')

    # Verify data source modifications
    self.assertIn('digest1', data)
    self.assertIn('digest3', data)
    self.assertNotIn('digest2', data)
    self.assertNotIn('digest4', data)

  def test_apply_node_predicate_sequence(self):
    wpid1 = ids.workplan(12345)
    wpid2 = ids.workplan(67890)

    wp1 = make_wp(wpid1, 100)
    c1 = make_check(wpid1, 'check1', 50)
    c1.options.add(digest='digest1')
    c1.options.add(digest='digest_shared')
    wp1.checks.append(c1)

    wp2 = make_wp(wpid2, 100)
    c2 = make_check(wpid2, 'check2', 50)
    c2.options.add(digest='digest2')
    c2.options.add(digest='digest_shared')
    wp2.checks.append(c2)

    data = value.LockedDataSource()
    vdata = value_data_pb2.ValueData()
    data['digest1'] = vdata
    data['digest2'] = vdata
    data['digest_shared'] = vdata

    # Keep only check1 (remove check2)
    transaction.apply_node_predicate(
        lambda _, node: node.identifier.id == 'check1',
        [wp1, wp2],
        data,
    )

    self.assertEqual(len(wp1.checks), 1)
    self.assertEqual(len(wp2.checks), 0)
    self.assertIn('digest1', data)
    self.assertIn('digest_shared', data)
    self.assertNotIn('digest2', data)


class TestTransactionalClient(unittest.TestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=client.TurboCITransport)
    # pylint: disable=unexpected-keyword-arg
    self.client = transaction.Transactional(
        wpid=self.wpid, transport=self.mock_transport
    )

  def test_assert_missing_nodes(self):
    self.client.assert_missing_nodes(
        ids.check('check1', self.wpid),
        ids.stage('stage1', self.wpid),
    )
    self.assertIn(
        ids.to_string(ids.check('check1')), self.client._observed.nodes
    )
    self.assertIn(
        ids.to_string(ids.stage('stage1')), self.client._observed.nodes
    )

  def test_observe_on_read(self):
    self.mock_transport.call_unary.return_value = (
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    self.mock_transport.call_unary.return_value.workplan.checks.append(
        make_check(self.wpid, 'check1', 50)
    )

    self.client.ReadWorkPlan(read_workplan_request_pb2.ReadWorkPlanRequest())

    self.assertEqual(self.client._observed._rev, make_rev(100))
    self.assertIn(
        ids.to_string(ids.check('check1')), self.client._observed.nodes
    )

  def test_write_nodes_injects_precondition_and_blocks_subsequent(self):
    self.client._observed.observe_ReadWorkPlan(
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    self.client._observed._observe(ids.check('check1', self.wpid))

    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse()
    )

    req = write_nodes_request_pb2.WriteNodesRequest()
    self.client.WriteNodes(req)

    self.assertTrue(req.HasField('txn'))
    self.assertEqual(req.txn.snapshot_version, make_rev(100))
    self.assertEqual(len(req.txn.nodes_observed), 1)
    self.assertEqual(req.txn.nodes_observed[0].check.id, 'check1')

    with self.assertRaisesRegex(
        client.TransactionMultipleWritesError,
        'transactional client used for more than one write',
    ):
      self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

  def test_write_nodes_failure_allows_retry(self):
    self.mock_transport.call_unary.side_effect = Exception('network error')

    with self.assertRaises(Exception):
      self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

    self.mock_transport.call_unary.side_effect = Exception(
        'another network error'
    )
    with self.assertRaisesRegex(Exception, 'another network error'):
      self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

    self.mock_transport.call_unary.side_effect = None
    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse()
    )
    self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

    with self.assertRaisesRegex(
        client.TransactionMultipleWritesError,
        'transactional client used for more than one write',
    ):
      self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

  def test_with_node_filter(self):
    filtered_client = self.client.with_node_filter(
        lambda _, node: node.identifier.id == 'check1'
    )

    self.assertNotEqual(self.client, filtered_client)
    self.assertIs(self.client._write_called, filtered_client._write_called)

    self.mock_transport.call_unary.return_value = (
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    self.mock_transport.call_unary.return_value.workplan.checks.append(
        make_check(self.wpid, 'check1', 50)
    )
    self.mock_transport.call_unary.return_value.workplan.checks.append(
        make_check(self.wpid, 'check2', 50)
    )

    self.mock_transport.call_unary.return_value.workplan.checks[0].options.add(
        digest='digest1'
    )
    self.mock_transport.call_unary.return_value.workplan.checks[1].options.add(
        digest='digest2'
    )

    filtered_client.data['digest1'] = value_data_pb2.ValueData()
    filtered_client.data['digest2'] = value_data_pb2.ValueData()

    filtered_client.ReadWorkPlan(
        read_workplan_request_pb2.ReadWorkPlanRequest()
    )

    self.assertIn(
        ids.to_string(ids.check('check1')), filtered_client._observed.nodes
    )
    self.assertNotIn(
        ids.to_string(ids.check('check2')), filtered_client._observed.nodes
    )

    self.assertIn('digest1', filtered_client.data)
    self.assertNotIn('digest2', filtered_client.data)

    self.mock_transport.call_unary.return_value = (
        write_nodes_response_pb2.WriteNodesResponse()
    )
    filtered_client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())

    with self.assertRaisesRegex(
        client.TransactionMultipleWritesError,
        'transactional client used for more than one write',
    ):
      self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())


class TestTransactionalClientAsync(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    # pylint: disable=unexpected-keyword-arg
    self.client = transaction.TransactionalAsync(
        wpid=self.wpid, transport=self.mock_transport
    )

  async def test_assert_missing_nodes(self):
    self.client.assert_missing_nodes(
        ids.check('check1', self.wpid),
        ids.stage('stage1', self.wpid),
    )
    self.assertIn(
        ids.to_string(ids.check('check1')), self.client._observed.nodes
    )
    self.assertIn(
        ids.to_string(ids.stage('stage1')), self.client._observed.nodes
    )

  async def test_observe_on_read(self):
    mock_response = read_workplan_response_pb2.ReadWorkPlanResponse(
        workplan=make_wp(self.wpid, 100)
    )
    mock_response.workplan.checks.append(make_check(self.wpid, 'check1', 50))
    self.mock_transport.call_unary = mock.AsyncMock(return_value=mock_response)

    await self.client.ReadWorkPlan(
        read_workplan_request_pb2.ReadWorkPlanRequest()
    )

    self.assertEqual(self.client._observed._rev, make_rev(100))
    self.assertIn(
        ids.to_string(ids.check('check1')), self.client._observed.nodes
    )

  async def test_write_nodes_injects_precondition_and_blocks_subsequent(self):
    self.client._observed.observe_ReadWorkPlan(
        read_workplan_response_pb2.ReadWorkPlanResponse(
            workplan=make_wp(self.wpid, 100)
        )
    )
    self.client._observed._observe(ids.check('check1', self.wpid))

    self.mock_transport.call_unary = mock.AsyncMock(
        return_value=write_nodes_response_pb2.WriteNodesResponse()
    )

    req = write_nodes_request_pb2.WriteNodesRequest()
    await self.client.WriteNodes(req)

    self.assertTrue(req.HasField('txn'))
    self.assertEqual(req.txn.snapshot_version, make_rev(100))
    self.assertEqual(len(req.txn.nodes_observed), 1)
    self.assertEqual(req.txn.nodes_observed[0].check.id, 'check1')

    with self.assertRaisesRegex(
        client.TransactionMultipleWritesError,
        'transactional client used for more than one write',
    ):
      await self.client.WriteNodes(write_nodes_request_pb2.WriteNodesRequest())


class TestRunTransaction(unittest.TestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=client.TurboCITransport)
    self.client = client.Sync(wpid=self.wpid, transport=self.mock_transport)

  def test_success(self):
    def cb(_):
      return 'success'

    res = transaction.run_transaction(self.client, cb)
    self.assertEqual(res, 'success')

  def test_retry_success(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger

    attempts = 0

    def cb(_):
      nonlocal attempts
      attempts += 1
      if attempts == 1:
        raise client.TransactionalPreconditionError.make('conflict')
      return 'success'

    res = transaction.run_transaction(self.client, cb, max_retries=3)
    self.assertEqual(res, 'success')
    self.assertEqual(attempts, 2)
    mock_logger.warning.assert_called_once_with(
        'Retrying transaction (attempt %d/%d) due to precondition conflict: %s',
        1,
        3,
        mock.ANY,
    )

  def test_max_retries_exceeded(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger

    attempts = 0

    def cb(_):
      nonlocal attempts
      attempts += 1
      raise client.TransactionalPreconditionError.make(f'conflict {attempts}')

    with self.assertRaisesRegex(client.RPCError, 'conflict 4'):
      transaction.run_transaction(self.client, cb, max_retries=3)
    self.assertEqual(attempts, 4)  # 1 initial + 3 retries
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            1,
            3,
            mock.ANY,
        ),
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            2,
            3,
            mock.ANY,
        ),
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            3,
            3,
            mock.ANY,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 3)

  def test_other_exception_no_retry(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger

    attempts = 0

    def cb(_):
      nonlocal attempts
      attempts += 1
      raise ValueError('some other error')

    with self.assertRaises(ValueError):
      transaction.run_transaction(self.client, cb, max_retries=3)
    self.assertEqual(attempts, 1)
    mock_logger.warning.assert_not_called()


class TestRunTransactionAsync(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    self.wpid = ids.workplan(12345)
    self.mock_transport = mock.Mock(spec=client.TurboCIAsyncTransport)
    self.client = client.Async(wpid=self.wpid, transport=self.mock_transport)

  async def test_success(self):
    async def cb(_):
      return 'success'

    res = await transaction.run_transaction_async(self.client, cb)
    self.assertEqual(res, 'success')

  async def test_retry_success(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger

    attempts = 0

    async def cb(_):
      nonlocal attempts
      attempts += 1
      if attempts == 1:
        raise client.TransactionalPreconditionError.make('conflict')
      return 'success'

    res = await transaction.run_transaction_async(
        self.client, cb, max_retries=3
    )
    self.assertEqual(res, 'success')
    self.assertEqual(attempts, 2)
    mock_logger.warning.assert_called_once_with(
        'Retrying transaction (attempt %d/%d) due to precondition conflict: %s',
        1,
        3,
        mock.ANY,
    )

  async def test_max_retries_exceeded(self):
    mock_logger = mock.Mock()
    self.client.logger = mock_logger

    attempts = 0

    async def cb(_):
      nonlocal attempts
      attempts += 1
      raise client.TransactionalPreconditionError.make(f'conflict {attempts}')

    with self.assertRaisesRegex(client.RPCError, 'conflict 4'):
      await transaction.run_transaction_async(self.client, cb, max_retries=3)
    self.assertEqual(attempts, 4)
    mock_logger.warning.assert_has_calls([
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            1,
            3,
            mock.ANY,
        ),
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            2,
            3,
            mock.ANY,
        ),
        mock.call(
            'Retrying transaction (attempt %d/%d) due to precondition'
            ' conflict: %s',
            3,
            3,
            mock.ANY,
        ),
    ])
    self.assertEqual(mock_logger.warning.call_count, 3)


if __name__ == '__main__':
  unittest.main()
