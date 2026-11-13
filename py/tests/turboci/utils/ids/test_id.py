# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for id utils."""

from __future__ import annotations

import copy
import unittest

from google.protobuf import timestamp_pb2

from testing.vectors.ids.to_from_string import test_case_pb2
from tests.turboci.utils.ids import test_to_from_vectors
from tests.turboci.utils.internal import test_vector
from turboci.graph.ids.v1 import identifier_kind_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils import ids as id_utils

_testTS = timestamp_pb2.Timestamp(seconds=12345, nanos=7890)

_test_idents: list[id_utils.SpecificIdentifier] = [
    identifier_pb2.WorkPlan(id='1234567'),
    identifier_pb2.Check(
        work_plan=identifier_pb2.WorkPlan(id='1234567'),
        id='cool/beans & stuff',
    ),
    identifier_pb2.CheckResult(
        check=identifier_pb2.Check(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            id='cool/beans & stuff',
        ),
        idx=3,
    ),
    identifier_pb2.CheckEdit(
        check=identifier_pb2.Check(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            id='cool/beans & stuff',
        ),
        version=_testTS,
    ),
    identifier_pb2.Stage(
        work_plan=identifier_pb2.WorkPlan(id='1234567'),
        is_worknode=True,
        id='938215823',
    ),
    identifier_pb2.Stage(
        work_plan=identifier_pb2.WorkPlan(id='1234567'),
        is_worknode=False,
        id='some stuff that is awesome',
    ),
    identifier_pb2.StageAttempt(
        stage=identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=True,
            id='938215823',
        ),
        idx=3,
    ),
    identifier_pb2.StageAttempt(
        stage=identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=False,
            id='some stuff that is awesome',
        ),
        idx=3,
    ),
    identifier_pb2.StageEdit(
        stage=identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=True,
            id='938215823',
        ),
        version=_testTS,
    ),
    identifier_pb2.StageEdit(
        stage=identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=False,
            id='some stuff that is awesome',
        ),
        version=_testTS,
    ),
    identifier_pb2.Check(
        id='cleared_check',
    ),
    identifier_pb2.CheckResult(
        check=identifier_pb2.Check(id='cleared_check'),
        idx=3,
    ),
    identifier_pb2.Stage(
        is_worknode=True,
        id='cleared_stage',
    ),
    identifier_pb2.StageAttempt(
        stage=identifier_pb2.Stage(is_worknode=False, id='cleared_stage'),
        idx=5,
    ),
]


class ToFromIDTest(unittest.TestCase):

  def test_vectors(self):
    def _check(tc: test_case_pb2.ToFromString) -> None:
      output = tc.output
      if output.err:
        with self.assertRaises(ValueError):
          id_utils.from_string(tc.input)
        return

      ident = id_utils.from_string(tc.input)
      self.assertEqual(ident, output.parsed)

      self.assertEqual(id_utils.to_string(ident), tc.input)
      self.assertEqual(id_utils.to_string_err(ident), tc.input)
      self.assertEqual(id_utils.kind_of(ident), output.kind)

      want_root = output.root
      want_wp = want_root.work_plan if want_root.HasField('work_plan') else None
      want_chk = want_root.check if want_root.HasField('check') else None
      want_stg = want_root.stage if want_root.HasField('stage') else None
      self.assertEqual(id_utils.root(ident), (want_wp, want_chk, want_stg))

      unwrapped = id_utils.unwrap(ident)
      if unwrapped is None:
        self.fail(f'unwrap({ident!r}) unexpectedly returned None')
      self.assertEqual(id_utils.wrap(ident), ident)
      self.assertEqual(id_utils.wrap(unwrapped), ident)
      self.assertEqual(id_utils.to_string(unwrapped), tc.input)
      self.assertEqual(id_utils.to_string_err(unwrapped), tc.input)
      self.assertEqual(id_utils.kind_of(unwrapped), output.kind)
      self.assertEqual(
          id_utils.root(unwrapped), (want_wp, want_chk, want_stg)
      )

    test_vector.run(
        self,
        test_to_from_vectors._TO_FROM_STRING_VECTORS,
        test_case_pb2.ToFromString,
        _check,
    )

  def test_unset_identifier(self):
    empty = identifier_pb2.Identifier()
    self.assertEqual(id_utils.wrap(empty), empty)
    self.assertIsNone(id_utils.unwrap(empty))
    self.assertEqual(
        id_utils.kind_of(empty),
        identifier_kind_pb2.IDENTIFIER_KIND_UNKNOWN,
    )
    self.assertEqual(id_utils.root(empty), (None, None, None))

  def test_to_string_edge_cases(self):
    self.assertEqual(
        id_utils.to_string(identifier_pb2.Identifier()),
        '<turboci invalid identifier: id could not be unwrapped>',
    )
    self.assertEqual(
        id_utils.to_string(identifier_pb2.WorkPlan()),
        '<turboci invalid identifier: id was empty>',
    )
    self.assertEqual(
        id_utils.to_string(identifier_pb2.WorkPlan(id='')),
        '<turboci invalid identifier: id was empty>',
    )
    self.assertEqual(
        id_utils.to_string(
            identifier_pb2.Identifier(work_plan=identifier_pb2.WorkPlan())
        ),
        '<turboci invalid identifier: id was empty>',
    )
    self.assertEqual(
        id_utils.to_string(
            identifier_pb2.Check(
                id='foo', work_plan=identifier_pb2.WorkPlan()
            )
        ),
        ':Cfoo',
    )
    self.assertEqual(
        id_utils.to_string(
            identifier_pb2.Identifier(
                check=identifier_pb2.Check(
                    id='foo', work_plan=identifier_pb2.WorkPlan(id='')
                )
            )
        ),
        ':Cfoo',
    )

  def test_to_string_err_edge_cases(self):
    self.assertTrue(issubclass(id_utils.InvalidIdentifierError, ValueError))
    for bad in (
        identifier_pb2.Identifier(),
        identifier_pb2.WorkPlan(),
        identifier_pb2.WorkPlan(id=''),
        identifier_pb2.Identifier(work_plan=identifier_pb2.WorkPlan()),
    ):
      with self.subTest(bad=bad):
        with self.assertRaises(id_utils.InvalidIdentifierError) as cm:
          id_utils.to_string_err(bad)
        self.assertIsInstance(cm.exception, ValueError)

    self.assertEqual(
        id_utils.to_string_err(
            identifier_pb2.Check(
                id='foo', work_plan=identifier_pb2.WorkPlan()
            )
        ),
        ':Cfoo',
    )
    self.assertEqual(
        id_utils.to_string_err(
            identifier_pb2.Identifier(
                check=identifier_pb2.Check(
                    id='foo', work_plan=identifier_pb2.WorkPlan(id='')
                )
            )
        ),
        ':Cfoo',
    )


class TestCreate(unittest.TestCase):

  def test_creators(self):
    def get_wp(
        msg: identifier_pb2.Check | identifier_pb2.Stage,
    ) -> identifier_pb2.WorkPlan | None:
      return msg.work_plan if msg.HasField('work_plan') else None

    for ident in _test_idents:
      with self.subTest(ident=id_utils.to_string(ident)):
        created_id = None
        match ident:
          case identifier_pb2.WorkPlan():
            created_id = id_utils.workplan(ident.id)
          case identifier_pb2.Check():
            created_id = id_utils.check(ident.id, get_wp(ident))
          case identifier_pb2.CheckResult():
            chk = ident.check
            created_id = id_utils.check_result(
                ident.idx, id_utils.check(chk.id, get_wp(chk))
            )
          case identifier_pb2.CheckEdit():
            chk = ident.check
            created_id = id_utils.check_edit(
                _testTS, id_utils.check(chk.id, in_workplan=get_wp(chk))
            )
          case identifier_pb2.Stage():
            created_id = id_utils.stage(
                ident.id,
                in_workplan=get_wp(ident),
                is_worknode=ident.is_worknode,
            )
          case identifier_pb2.StageAttempt():
            stg = ident.stage
            created_id = id_utils.stage_attempt(
                ident.idx,
                id_utils.stage(
                    stg.id,
                    in_workplan=get_wp(stg),
                    is_worknode=stg.is_worknode,
                ),
            )
          case identifier_pb2.StageEdit():
            stg = ident.stage
            created_id = id_utils.stage_edit(
                _testTS,
                id_utils.stage(
                    stg.id,
                    in_workplan=get_wp(stg),
                    is_worknode=stg.is_worknode,
                ),
            )
          case _:
            self.fail(f'unhandled type: {type(ident)}')

        self.assertEqual(created_id, ident)

  def test_check_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.check('a:b')

  def test_stage_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.stage('a:b')


class TestSetWorkplan(unittest.TestCase):

  def test_set_workplan_str(self):
    for ident in _test_idents:
      with self.subTest(ident=id_utils.to_string(ident)):
        new_workplan = id_utils.workplan('7654321')
        updated = id_utils.set_workplan(copy.deepcopy(ident), new_workplan.id)
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))

  def test_set_workplan_proto(self):
    for ident in _test_idents:
      with self.subTest(ident=id_utils.to_string(ident)):
        new_workplan = id_utils.workplan('7654321')
        updated = id_utils.set_workplan(copy.deepcopy(ident), new_workplan)
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))


class TestClearWorkplan(unittest.TestCase):

  def test_clear_workplan_unwrapped(self):
    for ident in _test_idents:
      with self.subTest(ident=id_utils.to_string(ident)):
        if isinstance(ident, identifier_pb2.WorkPlan):
          with self.assertRaises(NotImplementedError):
            id_utils.clear_workplan(copy.deepcopy(ident))
          continue

        updated = id_utils.clear_workplan(copy.deepcopy(ident))
        self.assert_workplan_cleared(updated)

  def test_clear_workplan_wrapped(self):
    for ident in _test_idents:
      with self.subTest(ident=id_utils.to_string(ident)):
        if isinstance(ident, identifier_pb2.WorkPlan):
          wrapped = id_utils.wrap(ident)
          with self.assertRaises(NotImplementedError):
            id_utils.clear_workplan(wrapped)
          continue

        wrapped = id_utils.wrap(copy.deepcopy(ident))
        updated = id_utils.clear_workplan(wrapped)
        self.assert_workplan_cleared(updated)

  def assert_workplan_cleared(self, ident: id_utils.AnyIdentifier) -> None:
    unwrapped = id_utils.unwrap(ident)
    match unwrapped:
      case identifier_pb2.Check() | identifier_pb2.Stage():
        self.assertFalse(unwrapped.HasField('work_plan'))
      case identifier_pb2.CheckResult() | identifier_pb2.CheckEdit():
        self.assertFalse(unwrapped.check.HasField('work_plan'))
      case identifier_pb2.StageAttempt() | identifier_pb2.StageEdit():
        self.assertFalse(unwrapped.stage.HasField('work_plan'))
      case _:
        self.fail(f'Unknown identifier type: {type(unwrapped)}')


class TestSameRoot(unittest.TestCase):

  def test_same_root_check(self):
    check1 = id_utils.check('hello')
    check_result1 = id_utils.check_result(3, check1)
    self.assertTrue(id_utils.same_root(check1, check_result1))

  def test_different_root_check(self):
    check1 = id_utils.check('hello')
    check_result2 = id_utils.check_result(3, id_utils.check('world'))
    self.assertFalse(id_utils.same_root(check1, check_result2))

  def test_same_root_stage(self):
    stage1 = id_utils.stage('hello', in_workplan=id_utils.workplan('123'))
    stage_attempt1 = id_utils.stage_attempt(2, stage1)
    self.assertTrue(id_utils.same_root(stage1, stage_attempt1))

  def test_different_root_stage(self):
    stage1 = id_utils.stage('hello', in_workplan=id_utils.workplan('123'))
    stage_attempt2 = id_utils.stage_attempt(
        2, id_utils.stage('world', in_workplan=id_utils.workplan('123'))
    )
    self.assertFalse(id_utils.same_root(stage1, stage_attempt2))

  def test_different_root_different_workplan(self):
    stage1 = id_utils.stage('hello', in_workplan=id_utils.workplan('123'))
    stage2 = id_utils.stage('hello', in_workplan=id_utils.workplan('456'))
    self.assertFalse(id_utils.same_root(stage1, stage2))

  def test_different_root(self):
    stage1 = id_utils.stage('hello', in_workplan=id_utils.workplan('123'))
    check2 = id_utils.check('goodbye')
    self.assertFalse(id_utils.same_root(stage1, check2))

  def test_workplan_has_no_root(self):
    wp1 = id_utils.workplan('123')
    wp2 = id_utils.workplan('456')
    self.assertFalse(id_utils.same_root(wp1, wp1))
    self.assertFalse(id_utils.same_root(wp1, wp2))
    self.assertFalse(id_utils.same_root(wp1, identifier_pb2.Identifier()))

  def test_same_workplan(self):
    wp1 = id_utils.workplan('123')
    wp2 = id_utils.workplan('456')
    c1 = id_utils.check('c1', in_workplan=wp1)
    c2 = id_utils.check('c2', in_workplan=wp1)
    c3 = id_utils.check('c1', in_workplan=wp2)
    c_no_wp1 = id_utils.check('c1')
    c_no_wp2 = id_utils.check('c2')

    self.assertTrue(id_utils.same_workplan(c1, c2))
    self.assertFalse(id_utils.same_workplan(c1, c3))
    self.assertFalse(id_utils.same_workplan(c1, identifier_pb2.Identifier()))
    self.assertFalse(id_utils.same_workplan(c_no_wp1, c_no_wp2))


if __name__ == '__main__':
  unittest.main()
