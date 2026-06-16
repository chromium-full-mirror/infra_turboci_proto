# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for transaction helpers."""

from __future__ import annotations

import unittest

from google.protobuf import timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import query_nodes_request_pb2
from turboci.graph.orchestrator.v1 import query_nodes_response_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2
from turboci.utils import client
from turboci.utils import ids
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
    self.ns.observe_read_work_plan(
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

    with self.assertRaises(client.TransactionalPreconditionError):
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

    with self.assertRaises(client.TransactionalPreconditionError):
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

    self.ns.observe_read_work_plan(rsp)

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

    self.ns.observe_query_nodes(req, rsp)

    self.assertEqual(self.ns._rev, wp.version)
    self.assertIn(ids.to_string(ids.check('check1')), self.ns.nodes)
    self.assertIn(ids.to_string(ids.stage('stage1')), self.ns.nodes)


if __name__ == '__main__':
  unittest.main()
