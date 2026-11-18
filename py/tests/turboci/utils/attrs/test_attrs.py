# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Behavior tests for turboci.utils.attrs."""

import unittest

from google.protobuf import message
from testing.vectors.attrs.create_attrs import test_case_pb2
from tests.turboci.utils.attrs.create_attrs_test_vectors import (
    _CREATE_ATTRS_TEST_VECTORS,
)
from tests.turboci.utils.internal import test_vector
from turboci.graph.orchestrator.v1 import attribute_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2
from turboci.utils import attrs


def _copy_input_write(
    call: test_case_pb2.CreateAttrs.Input,
) -> message.Message | None:
  """Returns a copy of the write passed to `add_*_attributes`, if any."""
  which = call.WhichOneof('call')
  if which == 'add_stage_attributes':
    add = call.add_stage_attributes
    if add.HasField('stage_write'):
      sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
      sw.CopyFrom(add.stage_write)
      return sw
  if which == 'add_check_attributes':
    add = call.add_check_attributes
    if add.HasField('check_write'):
      cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
      cw.CopyFrom(add.check_write)
      return cw
  return None


def _call(
    call: test_case_pb2.CreateAttrs.Input, write: message.Message | None
) -> message.Message | None:
  """Calls the function selected by `call`, passing `write` to `add_*`.

  Returns the created attribute, or `write` after `add_*_attributes`.
  """
  which = call.WhichOneof('call')
  if which == 'for_stage':
    fs = call.for_stage
    return attrs.for_stage(
        fs.name,
        fs.expression,
        on_state=fs.on_state if fs.HasField('on_state') else None,
        attribute_type=(
            fs.attribute_type if fs.HasField('attribute_type') else None
        ),
        indexed=fs.indexed if fs.HasField('indexed') else None,
    )
  if which == 'for_check':
    fc = call.for_check
    return attrs.for_check(
        fc.name,
        fc.expression,
        on_state=fc.on_state if fc.HasField('on_state') else None,
        attribute_type=(
            fc.attribute_type if fc.HasField('attribute_type') else None
        ),
        indexed=fc.indexed if fc.HasField('indexed') else None,
    )
  if which == 'add_stage_attributes':
    attrs.add_stage_attributes(
        write,  # type: ignore[arg-type]
        *call.add_stage_attributes.attributes,
    )
    return write
  if which == 'add_check_attributes':
    attrs.add_check_attributes(
        write,  # type: ignore[arg-type]
        *call.add_check_attributes.attributes,
    )
    return write
  raise AssertionError(f'test vector has no input call: {call}')


class TestCreateAttrsVectors(unittest.TestCase):
  """Runs the shared testing/vectors/attrs/create_attrs vectors."""

  def test_vectors(self):
    def _check(tc: test_case_pb2.CreateAttrs) -> None:
      write = _copy_input_write(tc.input)
      before = _copy_input_write(tc.input)

      if tc.HasField('err'):
        with self.assertRaises(ValueError) as cm:
          _call(tc.input, write)
        self.assertIn(tc.err, str(cm.exception))
        self.assertEqual(write, before, 'write was modified')
        return

      got = _call(tc.input, write)
      which = tc.output.WhichOneof('result')
      self.assertIsNotNone(which, 'test vector has no output result')
      self.assertEqual(got, getattr(tc.output, which))

    test_vector.run(
        self, _CREATE_ATTRS_TEST_VECTORS, test_case_pb2.CreateAttrs, _check
    )

# The tests below cover Python-only behavior that the shared vectors cannot
# express: enums passed as names or plain ints, and non-proto Python values.

_ATTRIBUTE_TYPE_NAMES = (
    (attribute_pb2.ATTRIBUTE_TYPE_BOOL, 'ATTRIBUTE_TYPE_BOOL'),
    (attribute_pb2.ATTRIBUTE_TYPE_BOOL_LIST, 'ATTRIBUTE_TYPE_BOOL_LIST'),
    (attribute_pb2.ATTRIBUTE_TYPE_INT64, 'ATTRIBUTE_TYPE_INT64'),
    (attribute_pb2.ATTRIBUTE_TYPE_INT64_LIST, 'ATTRIBUTE_TYPE_INT64_LIST'),
    (attribute_pb2.ATTRIBUTE_TYPE_STRING, 'ATTRIBUTE_TYPE_STRING'),
    (attribute_pb2.ATTRIBUTE_TYPE_STRING_LIST, 'ATTRIBUTE_TYPE_STRING_LIST'),
)

_INVALID_ATTRIBUTE_TYPE_NAMES = (
    ('BOOL', r'invalid attribute type: "BOOL"'),
    (
        'attribute_type_string',
        r'invalid attribute type: "attribute_type_string"',
    ),
    ('INVALID_TYPE', r'invalid attribute type: "INVALID_TYPE"'),
    (
        'ATTRIBUTE_TYPE_UNKNOWN',
        r'invalid attribute type: ATTRIBUTE_TYPE_UNKNOWN',
    ),
)

_INVALID_PYTHON_VALUES = (True, False, 3.14, [1])


class TestForStage(unittest.TestCase):
  """Python-only behavior of attrs.for_stage."""

  def test_on_state_accepts_enum_name_and_int(self):
    planned = stage_state_pb2.STAGE_STATE_PLANNED
    for on_state in ('STAGE_STATE_PLANNED', int(planned)):
      with self.subTest(on_state=on_state):
        attr = attrs.for_stage('my_team.attr', 'true', on_state=on_state)
        self.assertEqual(attr.on_state, planned)

  def test_invalid_on_state_name_raises_value_error(self):
    cases = (
        ('ATTEMPTING', r'invalid stage state: "ATTEMPTING"'),
        (
            'stage_state_attempting',
            r'invalid stage state: "stage_state_attempting"',
        ),
        ('STAGE_STATE_UNKNOWN', r'invalid stage state: STAGE_STATE_UNKNOWN'),
    )
    for on_state, want in cases:
      with self.subTest(on_state=on_state):
        with self.assertRaisesRegex(ValueError, want):
          attrs.for_stage('my_team.attr', 'true', on_state=on_state)

  def test_non_enum_on_state_raises_type_error(self):
    for value in _INVALID_PYTHON_VALUES:
      with self.subTest(value=value):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for on_state:'
        ):
          attrs.for_stage(
              'my_team.attr', 'true', on_state=value  # type: ignore
          )

  def test_attribute_type_accepts_enum_name(self):
    for want, name in _ATTRIBUTE_TYPE_NAMES:
      with self.subTest(attribute_type=name):
        attr = attrs.for_stage('my_team.attr', 'true', attribute_type=name)
        self.assertEqual(attr.attribute_type, want)

  def test_invalid_attribute_type_name_raises_value_error(self):
    for name, want in _INVALID_ATTRIBUTE_TYPE_NAMES:
      with self.subTest(attribute_type=name):
        with self.assertRaisesRegex(ValueError, want):
          attrs.for_stage('my_team.attr', 'true', attribute_type=name)

  def test_non_enum_attribute_type_raises_type_error(self):
    for value in _INVALID_PYTHON_VALUES:
      with self.subTest(value=value):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for attribute_type:'
        ):
          attrs.for_stage(
              'my_team.attr', 'true', attribute_type=value  # type: ignore
          )

  def test_non_string_name_raises_value_error(self):
    with self.assertRaisesRegex(
        ValueError, 'expected dot-separated lower_snake_case'
    ):
      attrs.for_stage(name=123, expression='true')  # type: ignore


class TestForCheck(unittest.TestCase):
  """Python-only behavior of attrs.for_check."""

  def test_on_state_accepts_enum_name_and_int(self):
    planned = check_state_pb2.CHECK_STATE_PLANNED
    for on_state in ('CHECK_STATE_PLANNED', int(planned)):
      with self.subTest(on_state=on_state):
        attr = attrs.for_check('my_team.attr', 'true', on_state=on_state)
        self.assertEqual(attr.on_state, planned)

  def test_invalid_on_state_name_raises_value_error(self):
    cases = (
        ('PLANNED', r'invalid check state: "PLANNED"'),
        (
            'check_state_planned',
            r'invalid check state: "check_state_planned"',
        ),
        ('CHECK_STATE_UNKNOWN', r'invalid check state: CHECK_STATE_UNKNOWN'),
    )
    for on_state, want in cases:
      with self.subTest(on_state=on_state):
        with self.assertRaisesRegex(ValueError, want):
          attrs.for_check('my_team.attr', 'true', on_state=on_state)

  def test_non_enum_on_state_raises_type_error(self):
    for value in _INVALID_PYTHON_VALUES:
      with self.subTest(value=value):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for on_state:'
        ):
          attrs.for_check(
              'my_team.attr', 'true', on_state=value  # type: ignore
          )

  def test_attribute_type_accepts_enum_name(self):
    for want, name in _ATTRIBUTE_TYPE_NAMES:
      with self.subTest(attribute_type=name):
        attr = attrs.for_check('my_team.attr', 'true', attribute_type=name)
        self.assertEqual(attr.attribute_type, want)

  def test_non_enum_attribute_type_raises_type_error(self):
    for value in _INVALID_PYTHON_VALUES:
      with self.subTest(value=value):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for attribute_type:'
        ):
          attrs.for_check(
              'my_team.attr', 'true', attribute_type=value  # type: ignore
          )

  def test_non_string_name_raises_value_error(self):
    with self.assertRaisesRegex(
        ValueError, 'expected dot-separated lower_snake_case'
    ):
      attrs.for_check(name=123, expression='true')  # type: ignore


class TestAddStageAttributes(unittest.TestCase):
  """Python-only behavior of attrs.add_stage_attributes."""

  def test_non_stage_write_target_raises_type_error(self):
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a = attrs.for_stage('my_team.a', 'true')
    with self.assertRaisesRegex(
        TypeError, r'expected StageWrite, got CheckWrite'
    ):
      attrs.add_stage_attributes(cw, a)  # type: ignore

  def test_none_attribute_raises_value_error(self):
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    with self.assertRaisesRegex(ValueError, 'attribute cannot be None'):
      attrs.add_stage_attributes(sw, None)  # type: ignore

  def test_check_attribute_raises_type_error(self):
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    ca = attrs.for_check('my_team.check_attr', 'true')
    with self.assertRaisesRegex(
        TypeError, r'expected StageAttributeWrite, got CheckAttributeWrite'
    ):
      attrs.add_stage_attributes(sw, ca)  # type: ignore


class TestAddCheckAttributes(unittest.TestCase):
  """Python-only behavior of attrs.add_check_attributes."""

  def test_non_check_write_target_raises_type_error(self):
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a = attrs.for_check('my_team.a', 'true')
    with self.assertRaisesRegex(
        TypeError, r'expected CheckWrite, got StageWrite'
    ):
      attrs.add_check_attributes(sw, a)  # type: ignore

  def test_none_attribute_raises_value_error(self):
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    with self.assertRaisesRegex(ValueError, 'attribute cannot be None'):
      attrs.add_check_attributes(cw, None)  # type: ignore

  def test_stage_attribute_raises_type_error(self):
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    sa = attrs.for_stage('my_team.stage_attr', 'true')
    with self.assertRaisesRegex(
        TypeError, r'expected CheckAttributeWrite, got StageAttributeWrite'
    ):
      attrs.add_check_attributes(cw, sa)  # type: ignore


if __name__ == '__main__':
  unittest.main()
