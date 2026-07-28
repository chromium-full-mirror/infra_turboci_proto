# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for value.iter."""

import unittest

from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import edit_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2
from turboci.utils import value


class TestIter(unittest.TestCase):
  # Piggyback on realm just to have unique keys for the valuerefs. Iterator
  # doesn't check for well-formed-ness of these things.

  def test_refs_in_stage(self):
    ref_args = value_ref_pb2.ValueRef(realm="stage_args")
    stage = stage_pb2.Stage(args=ref_args)

    ref_worknode = value_ref_pb2.ValueRef(realm="worknode")
    stage.legacy.worknode.CopyFrom(ref_worknode)

    ref_stage_edit_detail = value_ref_pb2.ValueRef(realm="stage_edit_detail")
    stage.edits.add().reason.details.append(ref_stage_edit_detail)
    stage.edits[0].stage.SetInParent()  # Tag edit as a stage edit.

    ref_attempt_detail = value_ref_pb2.ValueRef(realm="attempt_detail")
    attempt = stage.attempts.add(details=[ref_attempt_detail])

    ref_progress_detail = value_ref_pb2.ValueRef(realm="progress_detail")
    attempt.progress.add(details=[ref_progress_detail])

    self.assertEqual(
        list(value.refs_in_stage(stage)),
        [
            (value_slot_pb2.VALUE_SLOT_STAGE_ARGS, ref_args),
            (value_slot_pb2.VALUE_SLOT_STAGE_LEGACY_WORKNODE, ref_worknode),
            (
                value_slot_pb2.VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
                ref_stage_edit_detail,
            ),
            (value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL, ref_attempt_detail),
            (
                value_slot_pb2.VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
                ref_progress_detail,
            ),
        ],
    )

  def test_refs_in_stage_edit(self):
    edit = edit_pb2.Edit()

    ref_reason = value_ref_pb2.ValueRef(realm="reason")
    edit.reason.details.append(ref_reason)

    ref_attempt_detail = value_ref_pb2.ValueRef(realm="attempt_detail")
    edit.stage.attempts.add(details=[ref_attempt_detail])

    self.assertEqual(
        list(value.refs_in_edit(edit)),
        [
            (
                value_slot_pb2.VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
                ref_reason,
            ),
            (
                value_slot_pb2.VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
                ref_attempt_detail,
            ),
        ],
    )

  def test_refs_in_check_edit(self):
    edit = edit_pb2.Edit()

    ref_reason = value_ref_pb2.ValueRef(realm="reason")
    edit.reason.details.append(ref_reason)

    ref_option = value_ref_pb2.ValueRef(realm="option")
    edit.check.options.append(ref_option)

    ref_result_data = value_ref_pb2.ValueRef(realm="result_data")
    edit.check.results.add(data=[ref_result_data])

    self.assertEqual(
        list(value.refs_in_edit(edit)),
        [
            (
                value_slot_pb2.VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
                ref_reason,
            ),
            (value_slot_pb2.VALUE_SLOT_CHECK_EDIT_OPTION, ref_option),
            (
                value_slot_pb2.VALUE_SLOT_CHECK_EDIT_RESULT_DATA,
                ref_result_data,
            ),
        ],
    )

  def test_refs_in_check(self):
    check = check_pb2.Check()

    ref_option = value_ref_pb2.ValueRef(realm="option")
    check.options.append(ref_option)

    ref_result_data = value_ref_pb2.ValueRef(realm="result_data")
    check.results.add(data=[ref_result_data])

    ref_reason = value_ref_pb2.ValueRef(realm="reason")
    check.edits.add().reason.details.append(ref_reason)

    self.assertEqual(
        list(value.refs_in_check(check)),
        [
            (value_slot_pb2.VALUE_SLOT_CHECK_OPTION, ref_option),
            (value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA, ref_result_data),
            (
                value_slot_pb2.VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
                ref_reason,
            ),
        ],
    )

  def test_refs_in_workplan(self):
    wp = workplan_pb2.WorkPlan()

    ref_check_option = value_ref_pb2.ValueRef(realm="check_option")
    wp.checks.add(options=[ref_check_option])

    ref_stage_arg = value_ref_pb2.ValueRef(realm="stage_arg")
    wp.stages.add(args=ref_stage_arg)

    self.assertEqual(
        list(value.refs_in_workplan(wp)),
        [
            (value_slot_pb2.VALUE_SLOT_CHECK_OPTION, ref_check_option),
            (value_slot_pb2.VALUE_SLOT_STAGE_ARGS, ref_stage_arg),
        ],
    )


if __name__ == "__main__":
  unittest.main()
