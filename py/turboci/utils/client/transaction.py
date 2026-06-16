# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tracks observed nodes for transactions."""

from __future__ import annotations

import copy
import dataclasses

from google.protobuf import timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import query_nodes_request_pb2
from turboci.graph.orchestrator.v1 import query_nodes_response_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2
from turboci.utils import ids
from turboci.utils.client import errors

__all__ = [
    'ObservedNodeSet',
]

ObservableNode = stage_pb2.Stage | check_pb2.Check | stage_pb2.Stage.Attempt

ObservableNodeID = (
    identifier_pb2.Stage | identifier_pb2.Check | identifier_pb2.StageAttempt
)


@dataclasses.dataclass
class ObservedNodeSet:
  """Tracks nodes (checks, stages, attempts) observed as part of a transaction.

  This set can then be turned into a precondition for a WriteNodes request.
  """

  # The WorkPlan that this ObservedNodeSet is bound to.
  wpid: identifier_pb2.WorkPlan

  # The set of nodes observed - these are the identifiers of the nodes encoded
  # with `ids.to_string`.
  _nodes: set[str] = dataclasses.field(default_factory=set, init=False)

  # The revision of the workplan which we observed during the first observed
  # response.
  #
  # If we do a WriteNodes call with `_nodes` set, but this as `None`, it's the
  # same as asserting "the nodes do not exist".
  _rev: None | revision_pb2.Revision = dataclasses.field(
      default=None, init=False
  )

  @property
  def nodes(self) -> frozenset[str]:
    """Returns a read-only view of the observed nodes."""
    return frozenset(self._nodes)

  def assert_missing_nodes(self, *nodes: ObservableNodeID):
    """Adds `nodes` to our observed set as not existing in the WorkPlan yet.

    May only be used if `_rev` is None (i.e. no read/query has been done yet).

    If you want to query, then instead include these nodes as part of the
    query's nodes_by_id, and they will be marked as missing (if they actually
    are missing in the response).
    """
    if self._rev:
      raise ValueError('cannot assert_missing_nodes after doing read/query')
    for node in nodes:
      self._observe(node)

  def observe_query_nodes(
      self,
      req: query_nodes_request_pb2.QueryNodesRequest,
      rsp: query_nodes_response_pb2.QueryNodesResponse,
  ):
    """Adds all explicitly requested nodes, and all observed nodes to the set.

    Response and request must only contain nodes belonging to the
    ObservedNodeSet's bound WorkPlan.
    """
    for wp in rsp.workplans:
      self._observe_workplan(wp)
    for q in req.query:
      if q.HasField('nodes_by_id'):
        for node in q.nodes_by_id.nodes:
          match x := ids.unwrap(node):
            case (
                identifier_pb2.Stage()
                | identifier_pb2.StageAttempt()
                | identifier_pb2.Check()
            ):
              self._observe(x)

  def observe_read_work_plan(
      self,
      rsp: read_workplan_response_pb2.ReadWorkPlanResponse,
  ):
    """Adds all observed nodes to the set.

    Request must only contain nodes belonging to the ObservedNodeSet's bound
    WorkPlan.
    """
    self._observe_workplan(rsp.workplan)

  def _observe_workplan(self, wp: workplan_pb2.WorkPlan):
    """Adds all nodes in the WorkPlan to the observed set.

    If this is the first response observed, then `_rev` is set to `wp.version`.

    Otherwise, if any of the observed nodes have a version greater than
    `_rev`, this raises TransactionalPreconditionError.

    Raises:
      * ValueError if called after assert_missing_nodes.
      * ValueError if wp contains nodes from a different WorkPlan.
      * TransactionalPreconditionError if wp contains nodes whose version
        is greater than `_rev`.
    """
    if not self._rev:
      if self._nodes:
        raise ValueError('cannot read/query after `assert_missing_nodes`')
      self._rev = wp.version

    for check in wp.checks:
      self._assert_older_or_same(check)
      self._observe(check.identifier)

    for stage in wp.stages:
      self._assert_older_or_same(stage)
      self._observe(stage.identifier)

      for attempt in stage.attempts:
        if attempt.HasField('version'):
          self._assert_older_or_same(attempt)
          self._observe(attempt.identifier)

  def _assert_older_or_same(self, node: ObservableNode):
    assert self._rev
    if self._is_after(node.version, self._rev):
      cvers = self._ts_to_str(node.version.ts)
      wpvers = self._ts_to_str(self._rev.ts)
      ident = ids.to_string(node.identifier)
      raise errors.TransactionalPreconditionError(
          f'node[{ident!r}]: newer than snapshot: {cvers} > {wpvers}'
      )

  def _observe(self, ident: ObservableNodeID):
    """Observes a single node.

    If the node has a WorkPlan id, it must match the ObservedNodeSet's bound
    WorkPlan (or this will raise ValueError).

    Raises:
      * ValueError if wp contains nodes from a different WorkPlan.
    """
    curwp, _, _ = ids.root(ident)
    if curwp and curwp != self.wpid:
      cur, bound = ids.to_string(curwp), ids.to_string(self.wpid)
      raise ValueError(
          f'transaction observed multiple workplans: {cur!r} != {bound!r}'
      )
    elif curwp:
      ident = ids.clear_workplan(copy.deepcopy(ident))
    self._nodes.add(ids.to_string(ident))

  @staticmethod
  def _is_after(a: revision_pb2.Revision, b: revision_pb2.Revision) -> bool:
    return (a.ts.seconds, a.ts.nanos) > (b.ts.seconds, b.ts.nanos)

  @staticmethod
  def _ts_to_str(ts: timestamp_pb2.Timestamp) -> str:
    return f'{ts.seconds}/{ts.nanos}'
