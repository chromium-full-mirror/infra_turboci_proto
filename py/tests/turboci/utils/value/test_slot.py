# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for value.slot."""

import typing
import unittest

from turboci.graph.orchestrator.v1 import value_slot_pb2
from turboci.utils import value

# pylint: disable=protected-access


class TestValueRefSlotSet(unittest.TestCase):

  def test_zero_value(self):
    s = value.SlotSet()
    self.assertEqual(s._mask, 0)
    self.assertEqual(list(s), [])
    self.assertEqual(str(s), 'value.SlotSet{}')
    self.assertFalse(s.has_all(value_slot_pb2.VALUE_SLOT_CHECK_OPTION))
    self.assertFalse(s.has_any(value_slot_pb2.VALUE_SLOT_CHECK_OPTION))

  def test_initial_set(self):
    s = value.SlotSet(
        value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
        value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL,
    )
    self.assertTrue(
        s.has_all(
            value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
            value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL,
        )
    )
    self.assertTrue(s.has_any(value_slot_pb2.VALUE_SLOT_STAGE_ARGS))
    self.assertFalse(
        s.has_any(
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_RESULT_DATA,
            value_slot_pb2.VALUE_SLOT_STAGE_LEGACY_WORKNODE,
            value_slot_pb2.VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
            value_slot_pb2.VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
            value_slot_pb2.VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
        )
    )

  def test_set_unset_immutability(self):
    s1 = value.SlotSet()
    s2 = s1.set(
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
    )
    self.assertEqual(s1._mask, 0)
    self.assertEqual(s2._mask, (1 << 0) | (1 << 5))

    s3 = s2.unset(value_slot_pb2.VALUE_SLOT_CHECK_OPTION)
    self.assertEqual(s2._mask, (1 << 0) | (1 << 5))
    self.assertEqual(s3._mask, 1 << 5)

  def test_containment(self):
    s = value.SlotSet().set(
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
    )

    self.assertTrue(s.has_all(value_slot_pb2.VALUE_SLOT_CHECK_OPTION))
    self.assertTrue(
        s.has_all(
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
        )
    )
    self.assertFalse(
        s.has_all(
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
        )
    )

    self.assertTrue(s.has_any(value_slot_pb2.VALUE_SLOT_CHECK_OPTION))
    self.assertTrue(
        s.has_any(
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
        )
    )
    self.assertFalse(s.has_any(value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA))
    self.assertIn(value_slot_pb2.VALUE_SLOT_CHECK_OPTION, s)

  def test_unknown_and_duplicates(self):
    s = value.SlotSet().set(
        value_slot_pb2.VALUE_SLOT_UNKNOWN,
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
    )
    self.assertEqual(s._mask, 1 << 0)
    self.assertTrue(
        s.has_all(
            value_slot_pb2.VALUE_SLOT_UNKNOWN,
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        )
    )
    self.assertTrue(
        s.has_any(
            value_slot_pb2.VALUE_SLOT_UNKNOWN,
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        )
    )

  def test_out_of_bounds_errors(self):
    with self.assertRaises(ValueError):
      value.SlotSet().set(typing.cast(value_slot_pb2.ValueSlot, -1))
    with self.assertRaises(ValueError):
      value.SlotSet().set(
          typing.cast(
              value_slot_pb2.ValueSlot, value_slot_pb2.VALUE_SLOT_ALL + 1
          )
      )
    with self.assertRaises(ValueError):
      value.SlotSet().unset(
          typing.cast(
              value_slot_pb2.ValueSlot, value_slot_pb2.VALUE_SLOT_ALL + 1
          )
      )
    with self.assertRaises(ValueError):
      value.SlotSet().has_all(
          typing.cast(
              value_slot_pb2.ValueSlot, value_slot_pb2.VALUE_SLOT_ALL + 1
          )
      )
    with self.assertRaises(ValueError):
      value.SlotSet().has_any(
          typing.cast(
              value_slot_pb2.ValueSlot, value_slot_pb2.VALUE_SLOT_ALL + 1
          )
      )

  def test_slot_all(self):
    s = value.SlotSet().set(value_slot_pb2.VALUE_SLOT_ALL)
    self.assertEqual(s._mask, value.SlotSet._full_mask)
    self.assertTrue(s.has_all(value_slot_pb2.VALUE_SLOT_ALL))
    self.assertTrue(s.has_any(value_slot_pb2.VALUE_SLOT_ALL))

    self.assertTrue(
        s.has_all(
            value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_OPTION,
            value_slot_pb2.VALUE_SLOT_CHECK_EDIT_RESULT_DATA,
            value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
            value_slot_pb2.VALUE_SLOT_STAGE_LEGACY_WORKNODE,
            value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL,
            value_slot_pb2.VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
            value_slot_pb2.VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
            value_slot_pb2.VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
        )
    )

    s = s.unset(value_slot_pb2.VALUE_SLOT_ALL)
    self.assertEqual(s._mask, 0)
    self.assertFalse(s.has_all(value_slot_pb2.VALUE_SLOT_ALL))
    self.assertFalse(s.has_any(value_slot_pb2.VALUE_SLOT_ALL))

  def test_cross_language_invariance_vector(self):
    s = value.SlotSet().set(
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
        value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL,
        value_slot_pb2.VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
        value_slot_pb2.VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
        typing.cast(value_slot_pb2.ValueSlot, 64),
    )
    self.assertEqual(s._mask, 0x8000000000000583)

  def test_formatting(self):
    s = value.SlotSet().set(
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
    )
    self.assertEqual(str(s), 'value.SlotSet{CHECK_OPTION, STAGE_ARGS}')

  def test_round_trip(self):
    s1 = value.SlotSet().set(
        value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
        value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
        value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
    )
    s2 = value.SlotSet().set(*list(s1))
    self.assertEqual(s1, s2)


if __name__ == '__main__':
  unittest.main()
