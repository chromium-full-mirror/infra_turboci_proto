# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Test for id utils."""

from __future__ import annotations

import copy
import dataclasses
import unittest

from google.protobuf import timestamp_pb2
from turboci.graph.ids.v1 import identifier_kind_pb2
from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils import ids as id_utils

_testTS = timestamp_pb2.Timestamp(seconds=12345, nanos=7890)


@dataclasses.dataclass
class _id_test_case:
  ident: id_utils.AnyIdentifier
  ident_str: str
  note: str = ''

  @property
  def name(self):
    kind = self.kind_name()
    if self.note:
      return f'{kind} ({self.note})'
    return kind

  def kind_name(self) -> str:
    return id_utils.wrap(self.ident).WhichOneof('type')


_test_cases: list[_id_test_case] = [
    _id_test_case(identifier_pb2.WorkPlan(id='1234567'), 'L1234567'),
    _id_test_case(
        identifier_pb2.Check(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            id='cool/beans & stuff',
        ),
        'L1234567:Ccool/beans & stuff',
    ),
    _id_test_case(
        identifier_pb2.CheckResult(
            check=identifier_pb2.Check(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                id='cool/beans & stuff',
            ),
            idx=3,
        ),
        'L1234567:Ccool/beans & stuff:R3',
    ),
    _id_test_case(
        identifier_pb2.CheckEdit(
            check=identifier_pb2.Check(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                id='cool/beans & stuff',
            ),
            version=_testTS,
        ),
        'L1234567:Ccool/beans & stuff:V12345/7890',
    ),
    _id_test_case(
        identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=True,
            id='938215823',
        ),
        'L1234567:N938215823',
        note='worknode',
    ),
    _id_test_case(
        identifier_pb2.Stage(
            work_plan=identifier_pb2.WorkPlan(id='1234567'),
            is_worknode=False,
            id='some stuff that is awesome',
        ),
        'L1234567:Ssome stuff that is awesome',
    ),
    _id_test_case(
        identifier_pb2.StageAttempt(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                is_worknode=True,
                id='938215823',
            ),
            idx=3,
        ),
        'L1234567:N938215823:A3',
        note='worknode',
    ),
    _id_test_case(
        identifier_pb2.StageAttempt(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                is_worknode=False,
                id='some stuff that is awesome',
            ),
            idx=3,
        ),
        'L1234567:Ssome stuff that is awesome:A3',
    ),
    _id_test_case(
        identifier_pb2.StageEdit(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                is_worknode=True,
                id='938215823',
            ),
            version=_testTS,
        ),
        'L1234567:N938215823:V12345/7890',
        note='worknode',
    ),
    _id_test_case(
        identifier_pb2.StageEdit(
            stage=identifier_pb2.Stage(
                work_plan=identifier_pb2.WorkPlan(id='1234567'),
                is_worknode=False,
                id='some stuff that is awesome',
            ),
            version=_testTS,
        ),
        'L1234567:Ssome stuff that is awesome:V12345/7890',
    ),
    # Cleared (non-fully-qualified) identifier test cases
    _id_test_case(
        identifier_pb2.Check(
            id='cleared_check',
        ),
        ':Ccleared_check',
        note='cleared',
    ),
    _id_test_case(
        identifier_pb2.CheckResult(
            check=identifier_pb2.Check(id='cleared_check'),
            idx=3,
        ),
        ':Ccleared_check:R3',
        note='cleared',
    ),
    _id_test_case(
        identifier_pb2.Stage(
            is_worknode=True,
            id='cleared_stage',
        ),
        ':Ncleared_stage',
        note='cleared worknode',
    ),
    _id_test_case(
        identifier_pb2.StageAttempt(
            stage=identifier_pb2.Stage(is_worknode=False, id='cleared_stage'),
            idx=5,
        ),
        ':Scleared_stage:A5',
        note='cleared',
    ),
]


class ToFromIDTest(unittest.TestCase):

  def test_ok(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        self.assertEqual(id_utils.to_string(tc.ident), tc.ident_str)
        self.assertEqual(id_utils.to_string_err(tc.ident), tc.ident_str)
        self.assertEqual(
            id_utils.to_string(id_utils.wrap(tc.ident)), tc.ident_str
        )
        self.assertEqual(
            id_utils.to_string_err(id_utils.wrap(tc.ident)), tc.ident_str
        )
        self.assertEqual(
            id_utils.from_string(tc.ident_str), id_utils.wrap(tc.ident)
        )

  def test_from_string__invalid_stage_prefix__raises_value_error(self):
    invalid_cases = (
        ('L1234567:X938215823', 'stage'),
        (':Xcleared_stage', 'cleared stage'),
        ('L1234567:X938215823:A3', 'stage attempt'),
        ('L1234567:X938215823:V12345/7890', 'stage edit'),
    )

    for ident_str, desc in invalid_cases:
      with self.subTest(case=desc):
        with self.assertRaisesRegex(
            ValueError,
            r"^from_string: expected token to start with S, N or \?, got 'X'$",
        ):
          id_utils.from_string(ident_str)

  def test_from_string__unrecognized_id__raises_value_error(self):
    unrecognized_cases = (
        ('', 'empty string'),
        ('foo', 'unrecognized prefix'),
        ('L1234567:Cbeans:X', 'unrecognized check suffix'),
        ('L1234567:Cbeans:R3:extra', 'too many tokens'),
    )

    for ident_str, desc in unrecognized_cases:
      with self.subTest(case=desc):
        with self.assertRaisesRegex(
            ValueError,
            rf'^from_string: unrecognized ID {ident_str!r}$',
        ):
          id_utils.from_string(ident_str)

  def test_from_string_edge_cases(self):
    for bad in ('L', 'L:Cmeep', 'Cmeep', 'Lwp:C', 'Lwp:', 'Lwp:Cchk:R0', 'Lwp:Cchk:R-1'):
      with self.subTest(bad=bad):
        with self.assertRaises(ValueError):
          id_utils.from_string(bad)

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



class TestWrap(unittest.TestCase):

  def test_wrap(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        self.assertIsInstance(
            id_utils.wrap(tc.ident), identifier_pb2.Identifier
        )
        self.assertEqual(
            id_utils.wrap(tc.ident).WhichOneof('type'), tc.kind_name()
        )
        self.assertEqual(id_utils.unwrap(id_utils.wrap(tc.ident)), tc.ident)


class TestCreate(unittest.TestCase):

  def test_creators(self):
    def get_wp(msg):
      return msg.work_plan if msg.HasField('work_plan') else None

    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        created_id = None
        match tc.ident:
          case identifier_pb2.WorkPlan():
            created_id = id_utils.workplan(tc.ident.id)
          case identifier_pb2.Check():
            created_id = id_utils.check(tc.ident.id, get_wp(tc.ident))
          case identifier_pb2.CheckResult():
            chk = tc.ident.check
            created_id = id_utils.check_result(
                tc.ident.idx, id_utils.check(chk.id, get_wp(chk))
            )
          case identifier_pb2.CheckEdit():
            chk = tc.ident.check
            created_id = id_utils.check_edit(
                _testTS, id_utils.check(chk.id, in_workplan=get_wp(chk))
            )
          case identifier_pb2.Stage():
            created_id = id_utils.stage(
                tc.ident.id,
                in_workplan=get_wp(tc.ident),
                is_worknode=tc.ident.is_worknode,
            )
          case identifier_pb2.StageAttempt():
            stg = tc.ident.stage
            created_id = id_utils.stage_attempt(
                tc.ident.idx,
                id_utils.stage(
                    stg.id,
                    in_workplan=get_wp(stg),
                    is_worknode=stg.is_worknode,
                ),
            )
          case identifier_pb2.StageEdit():
            stg = tc.ident.stage
            created_id = id_utils.stage_edit(
                _testTS,
                id_utils.stage(
                    stg.id,
                    in_workplan=get_wp(stg),
                    is_worknode=stg.is_worknode,
                ),
            )
          case _:
            self.fail(f'unhandled type: {type(tc.ident)}')

        self.assertEqual(created_id, tc.ident)

  def test_check_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.check('a:b')

  def test_stage_id_no_colon(self):
    with self.assertRaisesRegex(ValueError, "must not contain ':'"):
      id_utils.stage('a:b')


class TestSetWorkplan(unittest.TestCase):

  def test_set_workplan_str(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        new_workplan = id_utils.workplan('7654321')
        updated = id_utils.set_workplan(
            copy.deepcopy(tc.ident), new_workplan.id
        )
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))

  def test_set_workplan_proto(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        new_workplan = id_utils.workplan('7654321')
        updated = id_utils.set_workplan(copy.deepcopy(tc.ident), new_workplan)
        # So this test also covers root and same_workplan.
        self.assertTrue(id_utils.same_workplan(updated, new_workplan))


class TestClearWorkplan(unittest.TestCase):

  def test_clear_workplan_unwrapped(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        if isinstance(tc.ident, identifier_pb2.WorkPlan):
          with self.assertRaises(NotImplementedError):
            id_utils.clear_workplan(copy.deepcopy(tc.ident))
          continue

        updated = id_utils.clear_workplan(copy.deepcopy(tc.ident))
        self.assert_workplan_cleared(updated)

  def test_clear_workplan_wrapped(self):
    for tc in _test_cases:
      with self.subTest(kind=tc.name):
        if isinstance(tc.ident, identifier_pb2.WorkPlan):
          wrapped = id_utils.wrap(tc.ident)
          with self.assertRaises(NotImplementedError):
            id_utils.clear_workplan(wrapped)
          continue

        wrapped = id_utils.wrap(copy.deepcopy(tc.ident))
        updated = id_utils.clear_workplan(wrapped)
        self.assert_workplan_cleared(updated)

  def assert_workplan_cleared(self, ident):
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
