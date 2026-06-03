# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for id utils."""

import unittest
import copy
from dataclasses import dataclass

from google.protobuf import timestamp_pb2

from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils import ids as id_utils

_testTS = timestamp_pb2.Timestamp(seconds=12345, nanos=7890)


@dataclass
class _id_test_case:
  kind: str
  ident: id_utils.AnyIdentifier
  ident_str: str
  note: str = ""

  @property
  def name(self):
    if self.note:
      return f'{self.kind} ({self.note})'
    return self.kind


_test_cases: list[_id_test_case] = [
    _id_test_case("work_plan", identifier_pb2.WorkPlan(id="1234567"),
                  "L1234567"),
    _id_test_case(
        "check",
        identifier_pb2.Check(
            work_plan=identifier_pb2.WorkPlan(id="1234567"),
            id="cool/beans & stuff",
        ), "L1234567:Ccool/beans & stuff"),
    _id_test_case(
        "check_result",
        identifier_pb2.CheckResult(
            check=identifier_pb2.Check(
                work_plan=identifier_pb2.WorkPlan(id="1234567"),
                id="cool/beans & stuff"),
            idx=3,
        ), "L1234567:Ccool/beans & stuff:R3"),
    _id_test_case(
        "check_edit",
        identifier_pb2.CheckEdit(check=identifier_pb2.Check(
            work_plan=identifier_pb2.WorkPlan(id="1234567"),
            id="cool/beans & stuff"),
                                 version=_testTS),
        "L1234567:Ccool/beans & stuff:V12345/7890"),
    _id_test_case(
        "stage",
        identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id="1234567"),
            is_worknode=True,
            id="938215823",
        ),
        "L1234567:N938215823",
        note="worknode",
    ),
    _id_test_case(
        "stage",
        identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id="1234567"),
            is_worknode=False,
            id="some stuff that is awesome",
        ),
        "L1234567:Ssome stuff that is awesome",
    ),
    _id_test_case(
        "stage_attempt",
        identifier_pb2.StageAttempt(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id="1234567"),
                is_worknode=True,
                id="938215823"),
            idx=3,
        ),
        "L1234567:N938215823:A3",
        note="worknode",
    ),
    _id_test_case(
        "stage_attempt",
        identifier_pb2.StageAttempt(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id="1234567"),
                is_worknode=False,
                id="some stuff that is awesome"),
            idx=3,
        ),
        "L1234567:Ssome stuff that is awesome:A3",
    ),
    _id_test_case(
        "stage_edit",
        identifier_pb2.StageEdit(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id="1234567"),
                is_worknode=True,
                id="938215823"),
            version=_testTS,
        ),
        "L1234567:N938215823:V12345/7890",
        note="worknode",
    ),
    _id_test_case(
        "stage_edit",
        identifier_pb2.StageEdit(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id="1234567"),
                is_worknode=False,
                id="some stuff that is awesome"),
            version=_testTS,
        ),
        "L1234567:Ssome stuff that is awesome:V12345/7890",
    ),
]


class ToFromIDTest(unittest.TestCase):

  def test_ok(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        self.assertEqual(id_utils.to_string(tc.ident), tc.ident_str)
        self.assertEqual(id_utils.to_string(id_utils.wrap(tc.ident)),
                         tc.ident_str)
        self.assertEqual(id_utils.from_string(tc.ident_str),
                         id_utils.wrap(tc.ident))


class TestWrap(unittest.TestCase):

  def test_wrap(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        self.assertIsInstance(id_utils.wrap(tc.ident),
                              identifier_pb2.Identifier)
        self.assertEqual(id_utils.wrap(tc.ident).WhichOneof('type'), tc.kind)
        self.assertEqual(id_utils.unwrap(id_utils.wrap(tc.ident)), tc.ident)


class TestCreate(unittest.TestCase):

  def test_creators(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        created_id = None
        match tc.kind:
          case "work_plan":
            created_id = id_utils.workplan(tc.ident.id)
          case "check":
            created_id = id_utils.check(tc.ident.id, tc.ident.work_plan)
          case "check_result":
            created_id = id_utils.check_result(
                tc.ident.idx,
                id_utils.check(tc.ident.check.id, tc.ident.check.work_plan))
          case "check_edit":
            created_id = id_utils.check_edit(
                _testTS,
                id_utils.check(tc.ident.check.id,
                               in_workplan=tc.ident.check.work_plan))
          case "stage":
            created_id = id_utils.stage(tc.ident.id,
                                        in_workplan=tc.ident.work_plan,
                                        is_worknode=tc.ident.is_worknode)
          case "stage_attempt":
            created_id = id_utils.stage_attempt(
                tc.ident.idx,
                id_utils.stage(tc.ident.stage.id,
                               in_workplan=tc.ident.stage.work_plan,
                               is_worknode=tc.ident.stage.is_worknode))
          case "stage_edit":
            created_id = id_utils.stage_edit(
                _testTS,
                id_utils.stage(tc.ident.stage.id,
                               in_workplan=tc.ident.stage.work_plan,
                               is_worknode=tc.ident.stage.is_worknode))

        self.assertEqual(created_id, tc.ident)

  def test_check_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.check("a:b")

  def test_stage_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.stage("a:b")


class TestSetWorkplan(unittest.TestCase):

  def test_set_workplan_str(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        new_workplan = id_utils.workplan("7654321")
        updated = id_utils.set_workplan(copy.deepcopy(tc.ident),
                                        new_workplan.id)
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))

  def test_set_workplan_proto(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        new_workplan = id_utils.workplan("7654321")
        updated = id_utils.set_workplan(copy.deepcopy(tc.ident), new_workplan)
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))


class TestSameRoot(unittest.TestCase):

  def test_same_root_check(self):
    check1 = id_utils.check("hello")
    check_result1 = id_utils.check_result(3, check1)
    self.assertTrue(id_utils.same_root(check1, check_result1))

  def test_different_root_check(self):
    check1 = id_utils.check("hello")
    check_result2 = id_utils.check_result(3, id_utils.check("world"))
    self.assertFalse(id_utils.same_root(check1, check_result2))

  def test_same_root_stage(self):
    stage1 = id_utils.stage("hello", in_workplan=id_utils.workplan("123"))
    stage_attempt1 = id_utils.stage_attempt(2, stage1)
    self.assertTrue(id_utils.same_root(stage1, stage_attempt1))

  def test_different_root_stage(self):
    stage1 = id_utils.stage("hello", in_workplan=id_utils.workplan("123"))
    stage_attempt2 = id_utils.stage_attempt(
        2, id_utils.stage("world", in_workplan=id_utils.workplan("123")))
    self.assertFalse(id_utils.same_root(stage1, stage_attempt2))

  def test_different_root_different_workplan(self):
    stage1 = id_utils.stage("hello", in_workplan=id_utils.workplan("123"))
    stage2 = id_utils.stage("hello", in_workplan=id_utils.workplan("456"))
    self.assertFalse(id_utils.same_root(stage1, stage2))

  def test_different_root(self):
    stage1 = id_utils.stage("hello", in_workplan=id_utils.workplan("123"))
    check2 = id_utils.check("goodbye")
    self.assertFalse(id_utils.same_root(stage1, check2))


if __name__ == '__main__':
  unittest.main()
