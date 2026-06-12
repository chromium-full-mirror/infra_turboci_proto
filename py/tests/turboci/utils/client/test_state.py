# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for client state."""

from __future__ import annotations

import copy
import unittest

from google.protobuf import any_pb2
from google.protobuf import empty_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.graph.orchestrator.v1 import allocate_worknode_ids_request_pb2
from turboci.graph.orchestrator.v1 import cancel_workplan_request_pb2
from turboci.graph.orchestrator.v1 import cancel_workplan_response_pb2
from turboci.graph.orchestrator.v1 import create_workplan_request_pb2
from turboci.graph.orchestrator.v1 import query_nodes_request_pb2
from turboci.graph.orchestrator.v1 import query_nodes_response_pb2
from turboci.graph.orchestrator.v1 import read_workplan_request_pb2
from turboci.graph.orchestrator.v1 import read_workplan_response_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2
from turboci.utils import value
from turboci.utils.client.state import State

# pylint: disable=protected-access


class TestState(unittest.TestCase):

  def setUp(self):
    self.wpid = identifier_pb2.WorkPlan(id='test-wpid')

  def test_adjust_request_token_injection(self):
    state = State(wpid=self.wpid, token='my-token')

    # Test all requests that need token
    reqs = [
        allocate_worknode_ids_request_pb2.AllocateWorkNodeIDsRequest(),
        cancel_workplan_request_pb2.CancelWorkPlanRequest(),
        query_nodes_request_pb2.QueryNodesRequest(),
        read_workplan_request_pb2.ReadWorkPlanRequest(),
        write_nodes_request_pb2.WriteNodesRequest(),
    ]

    for req in reqs:
      with self.subTest(req_type=type(req).__name__):
        self.assertEqual(req.token, '')
        state._adjust_request(req)
        self.assertEqual(req.token, 'my-token')

  def test_adjust_request_no_token(self):
    state = State(wpid=self.wpid, token=None)
    req = read_workplan_request_pb2.ReadWorkPlanRequest()
    state._adjust_request(req)
    self.assertEqual(req.token, '')

  def test_adjust_request_other_type_no_token_injection(self):
    state = State(wpid=self.wpid, token='my-token')
    req = create_workplan_request_pb2.CreateWorkPlanRequest()
    reqCopy = copy.deepcopy(req)
    # Should not raise exceptions.
    state._adjust_request(req)
    self.assertEqual(req, reqCopy)

  def test_adjust_request_default_known_types_read_workplan(self):
    default_types = value.TypeInfo(wanted=value.TypeSet([empty_pb2.Empty]))
    state = State(wpid=self.wpid, default_known_types=default_types)

    with self.subTest('without typeinfo'):
      req = read_workplan_request_pb2.ReadWorkPlanRequest()
      self.assertFalse(req.value_filter.HasField('type_info'))
      state._adjust_request(req)
      self.assertTrue(req.value_filter.HasField('type_info'))
      self.assertEqual(req.value_filter.type_info, default_types.to_proto())

    with self.subTest('with typeinfo'):
      req = read_workplan_request_pb2.ReadWorkPlanRequest()
      req.value_filter.type_info.unknown_jsonpb = True  # set something
      state._adjust_request(req)
      self.assertTrue(req.value_filter.HasField('type_info'))
      self.assertTrue(req.value_filter.type_info.unknown_jsonpb)
      self.assertNotEqual(req.value_filter.type_info, default_types.to_proto())

  def test_adjust_request_default_known_types_query_nodes(self):
    default_types = value.TypeInfo(wanted=value.TypeSet([empty_pb2.Empty]))
    state = State(wpid=self.wpid, default_known_types=default_types)

    with self.subTest('without type_info'):
      req = query_nodes_request_pb2.QueryNodesRequest()
      self.assertFalse(req.HasField('type_info'))
      state._adjust_request(req)
      self.assertTrue(req.HasField('type_info'))
      self.assertEqual(req.type_info, default_types.to_proto())

    with self.subTest('with type_info'):
      req = query_nodes_request_pb2.QueryNodesRequest()
      req.type_info.unknown_jsonpb = True  # set something
      state._adjust_request(req)
      self.assertTrue(req.HasField('type_info'))
      self.assertTrue(req.type_info.unknown_jsonpb)
      self.assertNotEqual(req.type_info, default_types.to_proto())

  def test_process_response(self):
    state = State(wpid=self.wpid)

    # Prepare some dummy value data
    apb = any_pb2.Any()
    apb.Pack(empty_pb2.Empty())
    val_data = value_data_pb2.ValueData(binary=apb)

    with self.subTest('ReadWorkPlanResponse'):
      state._process_response(
          read_workplan_request_pb2.ReadWorkPlanRequest(),
          read_workplan_response_pb2.ReadWorkPlanResponse(
              value_data={'digest1': val_data}
          ),
      )
      self.assertIn('digest1', state.data)
      self.assertEqual(state.data['digest1'], val_data)

    with self.subTest('QueryNodesResponse'):
      state._process_response(
          query_nodes_request_pb2.QueryNodesRequest(),
          query_nodes_response_pb2.QueryNodesResponse(
              value_data={'digest2': val_data}
          ),
      )
      self.assertIn('digest2', state.data)

    self.assertEqual(state.data['digest2'], val_data)
    self.assertIn('digest1', state.data)  # Should still be there

  def test_process_response_other_type(self):
    state = State(wpid=self.wpid)
    state._process_response(
        cancel_workplan_request_pb2.CancelWorkPlanRequest(),
        cancel_workplan_response_pb2.CancelWorkPlanResponse(),
    )
    self.assertEqual(len(state.data), 0)


if __name__ == '__main__':
  unittest.main()
