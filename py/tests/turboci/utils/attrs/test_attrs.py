# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Behavior tests for turboci.utils.attrs."""

import unittest

from turboci.graph.orchestrator.v1 import attribute_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2
from turboci.utils import attrs

_VALID_NAMES = (
    'foo.bar',
    'my_team.my_component.metric_count',
    'a.b.c',
    'step_1.val_2',
)

_INVALID_NAME_SYNTAX_CASES = (
    ('', 'empty string'),
    ('foo', 'un-namespaced name without dot'),
    ('foo.', 'trailing dot'),
    ('.foo', 'leading dot'),
    ('foo..bar', 'consecutive dots'),
    ('foo.Bar', 'uppercase segment'),
    ('Foo.bar', 'uppercase start'),
    ('_foo.bar', 'leading underscore in first segment'),
    ('foo._bar', 'leading underscore in second segment'),
    ('foo_.bar', 'trailing underscore in first segment'),
    ('foo.bar_', 'trailing underscore in second segment'),
    ('1foo.bar', 'leading digit in first segment'),
    ('foo.1bar', 'leading digit in second segment'),
    ('foo-bar.baz', 'hyphen'),
    ('foo.bar$', 'special character'),
)

_RESERVED_PREFIX_CASES = (
    ('check.foo', r"uses reserved prefix 'check\.'"),
    ('check.foo.bar', r"uses reserved prefix 'check\.'"),
    ('stage.foo', r"uses reserved prefix 'stage\.'"),
    ('stage.result', r"uses reserved prefix 'stage\.'"),
    ('work_node.foo', r"uses reserved prefix 'work_node\.'"),
    ('work_node.foo.bar', r"uses reserved prefix 'work_node\.'"),
    ('worknode.foo', r"uses reserved prefix 'worknode\.'"),
    ('worknode.foo.bar', r"uses reserved prefix 'worknode\.'"),
    ('work_plan.foo', r"uses reserved prefix 'work_plan\.'"),
    ('work_plan.foo.bar', r"uses reserved prefix 'work_plan\.'"),
    ('workplan.foo', r"uses reserved prefix 'workplan\.'"),
    ('workplan.foo.bar', r"uses reserved prefix 'workplan\.'"),
)

_VALID_ATTRIBUTE_TYPES = (
    (attribute_pb2.ATTRIBUTE_TYPE_BOOL, 'ATTRIBUTE_TYPE_BOOL'),
    (attribute_pb2.ATTRIBUTE_TYPE_BOOL_LIST, 'ATTRIBUTE_TYPE_BOOL_LIST'),
    (attribute_pb2.ATTRIBUTE_TYPE_INT64, 'ATTRIBUTE_TYPE_INT64'),
    (attribute_pb2.ATTRIBUTE_TYPE_INT64_LIST, 'ATTRIBUTE_TYPE_INT64_LIST'),
    (attribute_pb2.ATTRIBUTE_TYPE_STRING, 'ATTRIBUTE_TYPE_STRING'),
    (attribute_pb2.ATTRIBUTE_TYPE_STRING_LIST, 'ATTRIBUTE_TYPE_STRING_LIST'),
)

_INVALID_ATTRIBUTE_TYPE_VALUES = (
    ('BOOL', r"invalid attribute type: 'BOOL'", 'short name'),
    (
        'attribute_type_string',
        r"invalid attribute type: 'attribute_type_string'",
        'lowercase',
    ),
    (
        'INVALID_TYPE',
        r"invalid attribute type: 'INVALID_TYPE'",
        'unrecognized string',
    ),
    (99999, r'invalid attribute type: 99999', 'unrecognized enum integer'),
    (
        attribute_pb2.ATTRIBUTE_TYPE_UNKNOWN,
        r'invalid attribute type: 0',
        'unknown type',
    ),
)


class TestForStage(unittest.TestCase):
  """Behavior tests for attrs.for_stage."""

  def test_default_on_state_left_unset_when_omitted(self):
    # Arrange
    name = 'my_team.has_flag'
    expr = 'tags.stage.attempt.detail.ready == true'

    # Act
    attr = attrs.for_stage(name=name, expression=expr)

    # Assert
    self.assertIsInstance(
        attr, write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite
    )
    self.assertEqual(attr.name, name)
    self.assertEqual(attr.expression, expr)
    self.assertFalse(attr.HasField('on_state'))
    self.assertFalse(attr.HasField('attribute_type'))

  def test_unknown_on_state_raises_value_error(self):
    # Arrange
    name = 'my_team.has_flag'
    expr = 'true'

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r'cannot use STAGE_STATE_UNKNOWN as on_state'
    ):
      attrs.for_stage(
          name=name,
          expression=expr,
          on_state=stage_state_pb2.STAGE_STATE_UNKNOWN,
      )

    with self.assertRaisesRegex(
        ValueError, r'cannot use STAGE_STATE_UNKNOWN as on_state'
    ):
      attrs.for_stage(
          name=name,
          expression=expr,
          on_state='STAGE_STATE_UNKNOWN',
      )

  def test_explicit_valid_stage_states_accepted(self):
    # Arrange
    cases = (
        (
            stage_state_pb2.STAGE_STATE_PLANNED,
            stage_state_pb2.STAGE_STATE_PLANNED,
            'enum PLANNED',
        ),
        (
            'STAGE_STATE_PLANNED',
            stage_state_pb2.STAGE_STATE_PLANNED,
            'str PLANNED',
        ),
        (
            stage_state_pb2.STAGE_STATE_ATTEMPTING,
            stage_state_pb2.STAGE_STATE_ATTEMPTING,
            'enum ATTEMPTING',
        ),
        (
            'STAGE_STATE_ATTEMPTING',
            stage_state_pb2.STAGE_STATE_ATTEMPTING,
            'str ATTEMPTING',
        ),
        (
            stage_state_pb2.STAGE_STATE_AWAITING_GROUP,
            stage_state_pb2.STAGE_STATE_AWAITING_GROUP,
            'enum AWAITING_GROUP',
        ),
        (
            'STAGE_STATE_AWAITING_GROUP',
            stage_state_pb2.STAGE_STATE_AWAITING_GROUP,
            'str AWAITING_GROUP',
        ),
        (
            stage_state_pb2.STAGE_STATE_FINAL,
            stage_state_pb2.STAGE_STATE_FINAL,
            'enum FINAL',
        ),
        (
            'STAGE_STATE_FINAL',
            stage_state_pb2.STAGE_STATE_FINAL,
            'str FINAL',
        ),
    )

    # Act & Assert
    for state_input, expected_state, desc in cases:
      with self.subTest(desc=desc):
        attr = attrs.for_stage(
            name='my_team.attr',
            expression='true',
            on_state=state_input,
        )
        self.assertEqual(attr.on_state, expected_state)

  def test_valid_attribute_types_set_type_field(self):
    # Arrange & Act & Assert
    for enum_val, str_name in _VALID_ATTRIBUTE_TYPES:
      with self.subTest(attr_type=str_name, as_enum=True):
        attr = attrs.for_stage(
            name='my_team.attr',
            expression='true',
            attribute_type=enum_val,
        )
        self.assertEqual(attr.attribute_type, enum_val)

      with self.subTest(attr_type=str_name, as_str=True):
        attr = attrs.for_stage(
            name='my_team.attr',
            expression='true',
            attribute_type=str_name,
        )
        self.assertEqual(attr.attribute_type, enum_val)

  def test_none_attribute_type_leaves_field_unset(self):
    # Arrange & Act
    attr = attrs.for_stage(
        name='my_team.attr',
        expression='true',
        attribute_type=None,
    )

    # Assert
    self.assertFalse(attr.HasField('attribute_type'))

  def test_valid_namespaced_names_accepted(self):
    # Arrange & Act & Assert
    for name in _VALID_NAMES:
      with self.subTest(name=name):
        attr = attrs.for_stage(name=name, expression='true')
        self.assertEqual(attr.name, name)

  def test_invalid_attribute_name_syntax_raises_value_error(self):
    # Arrange & Act & Assert
    for name, reason in _INVALID_NAME_SYNTAX_CASES:
      with self.subTest(name=name, reason=reason):
        with self.assertRaisesRegex(
            ValueError, 'expected dot-separated lower_snake_case'
        ):
          attrs.for_stage(name=name, expression='true')

  def test_reserved_attribute_name_prefix_raises_value_error(self):
    # Arrange & Act & Assert
    for name, expected_regex in _RESERVED_PREFIX_CASES:
      with self.subTest(name=name):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_stage(name=name, expression='true')

  def test_non_string_attribute_name_raises_value_error(self):
    # Arrange & Act & Assert
    with self.assertRaisesRegex(
        ValueError, 'expected dot-separated lower_snake_case'
    ):
      attrs.for_stage(name=123, expression='true')  # type: ignore

  def test_empty_expression_raises_value_error(self):
    # Arrange & Act & Assert
    with self.assertRaisesRegex(ValueError, 'expression cannot be empty'):
      attrs.for_stage(name='my_team.attr', expression='')

  def test_invalid_stage_state_value_raises_value_error(self):
    # Arrange
    invalid_states = (
        ('ATTEMPTING', r"unknown stage state name: 'ATTEMPTING'"),
        (
            'stage_state_attempting',
            r"unknown stage state name: 'stage_state_attempting'",
        ),
        (
            'INVALID_STAGE_STATE',
            r"unknown stage state name: 'INVALID_STAGE_STATE'",
        ),
        (99999, r'unknown stage state value: 99999'),
    )

    # Act & Assert
    for state, expected_regex in invalid_states:
      with self.subTest(state=state):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_stage(
              name='my_team.attr',
              expression='true',
              on_state=state,
          )

  def test_invalid_stage_state_python_type_raises_type_error(self):
    # Arrange & Act & Assert
    for invalid_val in (True, False, 3.14, [1]):
      with self.subTest(val=invalid_val):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for on_state:'
        ):
          attrs.for_stage(
              name='my_team.attr',
              expression='true',
              on_state=invalid_val,  # type: ignore
          )

  def test_invalid_attribute_type_value_raises_value_error(self):
    # Arrange & Act & Assert
    for attr_type, expected_regex, reason in _INVALID_ATTRIBUTE_TYPE_VALUES:
      with self.subTest(attr_type=attr_type, reason=reason):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_stage(
              name='my_team.attr',
              expression='true',
              attribute_type=attr_type,
          )

  def test_invalid_attribute_type_python_type_raises_type_error(self):
    # Arrange & Act & Assert
    for invalid_val in (True, False, 3.14, [1]):
      with self.subTest(val=invalid_val):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for attribute_type:'
        ):
          attrs.for_stage(
              name='my_team.attr',
              expression='true',
              attribute_type=invalid_val,  # type: ignore
          )


class TestForCheck(unittest.TestCase):
  """Behavior tests for attrs.for_check."""

  def test_default_on_state_left_unset_when_omitted(self):
    # Arrange
    name = 'my_team.has_flag'
    expr = 'tags.check.result.data.passed == true'

    # Act
    attr = attrs.for_check(name=name, expression=expr)

    # Assert
    self.assertIsInstance(
        attr, write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite
    )
    self.assertEqual(attr.name, name)
    self.assertEqual(attr.expression, expr)
    self.assertFalse(attr.HasField('on_state'))
    self.assertFalse(attr.HasField('attribute_type'))

  def test_unknown_on_state_raises_value_error(self):
    # Arrange
    name = 'my_team.has_flag'
    expr = 'true'

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r'cannot use CHECK_STATE_UNKNOWN as on_state'
    ):
      attrs.for_check(
          name=name,
          expression=expr,
          on_state=check_state_pb2.CHECK_STATE_UNKNOWN,
      )

    with self.assertRaisesRegex(
        ValueError, r'cannot use CHECK_STATE_UNKNOWN as on_state'
    ):
      attrs.for_check(
          name=name,
          expression=expr,
          on_state='CHECK_STATE_UNKNOWN',
      )

  def test_explicit_valid_check_states_accepted(self):
    # Arrange
    cases = (
        (
            check_state_pb2.CHECK_STATE_PLANNED,
            check_state_pb2.CHECK_STATE_PLANNED,
            'enum PLANNED',
        ),
        (
            'CHECK_STATE_PLANNED',
            check_state_pb2.CHECK_STATE_PLANNED,
            'str PLANNED',
        ),
        (
            check_state_pb2.CHECK_STATE_FINAL,
            check_state_pb2.CHECK_STATE_FINAL,
            'enum FINAL',
        ),
        (
            'CHECK_STATE_FINAL',
            check_state_pb2.CHECK_STATE_FINAL,
            'str FINAL',
        ),
    )

    # Act & Assert
    for state_input, expected_state, desc in cases:
      with self.subTest(desc=desc):
        attr = attrs.for_check(
            name='my_team.attr',
            expression='true',
            on_state=state_input,
        )
        self.assertEqual(attr.on_state, expected_state)

  def test_valid_attribute_types_set_type_field(self):
    # Arrange & Act & Assert
    for enum_val, str_name in _VALID_ATTRIBUTE_TYPES:
      with self.subTest(attr_type=str_name, as_enum=True):
        attr = attrs.for_check(
            name='my_team.attr',
            expression='true',
            attribute_type=enum_val,
        )
        self.assertEqual(attr.attribute_type, enum_val)

      with self.subTest(attr_type=str_name, as_str=True):
        attr = attrs.for_check(
            name='my_team.attr',
            expression='true',
            attribute_type=str_name,
        )
        self.assertEqual(attr.attribute_type, enum_val)

  def test_none_attribute_type_leaves_field_unset(self):
    # Arrange & Act
    attr = attrs.for_check(
        name='my_team.attr',
        expression='true',
        attribute_type=None,
    )

    # Assert
    self.assertFalse(attr.HasField('attribute_type'))

  def test_valid_namespaced_names_accepted(self):
    # Arrange & Act & Assert
    for name in _VALID_NAMES:
      with self.subTest(name=name):
        attr = attrs.for_check(name=name, expression='true')
        self.assertEqual(attr.name, name)

  def test_invalid_attribute_name_syntax_raises_value_error(self):
    # Arrange & Act & Assert
    for name, reason in _INVALID_NAME_SYNTAX_CASES:
      with self.subTest(name=name, reason=reason):
        with self.assertRaisesRegex(
            ValueError, 'expected dot-separated lower_snake_case'
        ):
          attrs.for_check(name=name, expression='true')

  def test_reserved_attribute_name_prefix_raises_value_error(self):
    # Arrange & Act & Assert
    for name, expected_regex in _RESERVED_PREFIX_CASES:
      with self.subTest(name=name):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_check(name=name, expression='true')

  def test_non_string_attribute_name_raises_value_error(self):
    # Arrange & Act & Assert
    with self.assertRaisesRegex(
        ValueError, 'expected dot-separated lower_snake_case'
    ):
      attrs.for_check(name=123, expression='true')  # type: ignore

  def test_empty_expression_raises_value_error(self):
    # Arrange & Act & Assert
    with self.assertRaisesRegex(ValueError, 'expression cannot be empty'):
      attrs.for_check(name='my_team.attr', expression='')

  def test_invalid_check_state_value_raises_value_error(self):
    # Arrange
    invalid_states = (
        ('PLANNED', r"unknown check state name: 'PLANNED'"),
        (
            'check_state_planned',
            r"unknown check state name: 'check_state_planned'",
        ),
        (
            'INVALID_CHECK_STATE',
            r"unknown check state name: 'INVALID_CHECK_STATE'",
        ),
        (99999, r'unknown check state value: 99999'),
    )

    # Act & Assert
    for state, expected_regex in invalid_states:
      with self.subTest(state=state):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_check(
              name='my_team.attr',
              expression='true',
              on_state=state,
          )

  def test_invalid_check_state_python_type_raises_type_error(self):
    # Arrange & Act & Assert
    for invalid_val in (True, False, 3.14, [1]):
      with self.subTest(val=invalid_val):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for on_state:'
        ):
          attrs.for_check(
              name='my_team.attr',
              expression='true',
              on_state=invalid_val,  # type: ignore
          )

  def test_invalid_attribute_type_value_raises_value_error(self):
    # Arrange & Act & Assert
    for attr_type, expected_regex, reason in _INVALID_ATTRIBUTE_TYPE_VALUES:
      with self.subTest(attr_type=attr_type, reason=reason):
        with self.assertRaisesRegex(ValueError, expected_regex):
          attrs.for_check(
              name='my_team.attr',
              expression='true',
              attribute_type=attr_type,
          )

  def test_invalid_attribute_type_python_type_raises_type_error(self):
    # Arrange & Act & Assert
    for invalid_val in (True, False, 3.14, [1]):
      with self.subTest(val=invalid_val):
        with self.assertRaisesRegex(
            TypeError, r'unexpected type for attribute_type:'
        ):
          attrs.for_check(
              name='my_team.attr',
              expression='true',
              attribute_type=invalid_val,  # type: ignore
          )


class TestAddStageAttributes(unittest.TestCase):
  """Behavior tests for attrs.add_stage_attributes."""

  def test_multiple_valid_attributes_appended_to_stage_write(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a1 = attrs.for_stage(
        'my_team.a', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )
    a2 = attrs.for_stage(
        'my_team.b', 'exp2', stage_state_pb2.STAGE_STATE_FINAL
    )

    # Act
    attrs.add_stage_attributes(sw, a1, a2)

    # Assert
    self.assertEqual(len(sw.attributes), 2)
    self.assertEqual(sw.attributes[0].name, 'my_team.a')
    self.assertEqual(sw.attributes[1].name, 'my_team.b')

  def test_subsequent_call_appends_to_existing_attributes(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a1 = attrs.for_stage(
        'my_team.a', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )
    attrs.add_stage_attributes(sw, a1)
    a2 = attrs.for_stage(
        'my_team.b', 'exp2', stage_state_pb2.STAGE_STATE_FINAL
    )

    # Act
    attrs.add_stage_attributes(sw, a2)

    # Assert
    self.assertEqual(len(sw.attributes), 2)
    self.assertEqual(sw.attributes[0].name, 'my_team.a')
    self.assertEqual(sw.attributes[1].name, 'my_team.b')

  def test_duplicate_names_in_call_raises_value_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a1 = attrs.for_stage(
        'my_team.dup', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )
    a2 = attrs.for_stage(
        'my_team.dup', 'exp2', stage_state_pb2.STAGE_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_stage_attributes(sw, a1, a2)

  def test_duplicate_name_with_existing_attribute_raises_value_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a1 = attrs.for_stage(
        'my_team.dup', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )
    attrs.add_stage_attributes(sw, a1)
    a2 = attrs.for_stage(
        'my_team.dup', 'exp2', stage_state_pb2.STAGE_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_stage_attributes(sw, a2)

  def test_preexisting_duplicate_names_in_stage_write_raises_value_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a1 = attrs.for_stage(
        'my_team.dup', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )
    a2 = attrs.for_stage(
        'my_team.dup', 'exp2', stage_state_pb2.STAGE_STATE_FINAL
    )
    sw.attributes.extend([a1, a2])
    a3 = attrs.for_stage(
        'my_team.other', 'exp3', stage_state_pb2.STAGE_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_stage_attributes(sw)

    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_stage_attributes(sw, a3)

    self.assertEqual(len(sw.attributes), 2)

  def test_non_stage_write_target_raises_type_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a = attrs.for_stage(
        'my_team.a', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )

    # Act & Assert
    with self.assertRaisesRegex(
        TypeError, r'expected StageWrite, got CheckWrite'
    ):
      attrs.add_stage_attributes(cw, a)  # type: ignore

  def test_none_stage_write_target_raises_value_error(self):
    # Arrange
    a = attrs.for_stage(
        'my_team.a', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )

    # Act & Assert
    with self.assertRaisesRegex(ValueError, 'stage_write cannot be None'):
      attrs.add_stage_attributes(None, a)  # type: ignore

  def test_none_attribute_raises_value_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()

    # Act & Assert
    with self.assertRaisesRegex(ValueError, 'attribute cannot be None'):
      attrs.add_stage_attributes(sw, None)  # type: ignore

  def test_incompatible_attribute_type_raises_type_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    ca = attrs.for_check(
        'my_team.check_attr', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )

    # Act & Assert
    with self.assertRaisesRegex(
        TypeError, r'expected StageAttributeWrite, got CheckAttributeWrite'
    ):
      attrs.add_stage_attributes(sw, ca)  # type: ignore


class TestAddCheckAttributes(unittest.TestCase):
  """Behavior tests for attrs.add_check_attributes."""

  def test_multiple_valid_attributes_appended_to_check_write(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a1 = attrs.for_check(
        'my_team.a', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )
    a2 = attrs.for_check(
        'my_team.b', 'exp2', check_state_pb2.CHECK_STATE_FINAL
    )

    # Act
    attrs.add_check_attributes(cw, a1, a2)

    # Assert
    self.assertEqual(len(cw.attributes), 2)
    self.assertEqual(cw.attributes[0].name, 'my_team.a')
    self.assertEqual(cw.attributes[1].name, 'my_team.b')

  def test_subsequent_call_appends_to_existing_attributes(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a1 = attrs.for_check(
        'my_team.a', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )
    attrs.add_check_attributes(cw, a1)
    a2 = attrs.for_check(
        'my_team.b', 'exp2', check_state_pb2.CHECK_STATE_FINAL
    )

    # Act
    attrs.add_check_attributes(cw, a2)

    # Assert
    self.assertEqual(len(cw.attributes), 2)
    self.assertEqual(cw.attributes[0].name, 'my_team.a')
    self.assertEqual(cw.attributes[1].name, 'my_team.b')

  def test_duplicate_names_in_call_raises_value_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a1 = attrs.for_check(
        'my_team.dup', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )
    a2 = attrs.for_check(
        'my_team.dup', 'exp2', check_state_pb2.CHECK_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_check_attributes(cw, a1, a2)

  def test_duplicate_name_with_existing_attribute_raises_value_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a1 = attrs.for_check(
        'my_team.dup', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )
    attrs.add_check_attributes(cw, a1)
    a2 = attrs.for_check(
        'my_team.dup', 'exp2', check_state_pb2.CHECK_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_check_attributes(cw, a2)

  def test_preexisting_duplicate_names_in_check_write_raises_value_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    a1 = attrs.for_check(
        'my_team.dup', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )
    a2 = attrs.for_check(
        'my_team.dup', 'exp2', check_state_pb2.CHECK_STATE_FINAL
    )
    cw.attributes.extend([a1, a2])
    a3 = attrs.for_check(
        'my_team.other', 'exp3', check_state_pb2.CHECK_STATE_FINAL
    )

    # Act & Assert
    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_check_attributes(cw)

    with self.assertRaisesRegex(
        ValueError, r"duplicate attribute name: 'my_team\.dup'"
    ):
      attrs.add_check_attributes(cw, a3)

    self.assertEqual(len(cw.attributes), 2)

  def test_non_check_write_target_raises_type_error(self):
    # Arrange
    sw = write_nodes_request_pb2.WriteNodesRequest.StageWrite()
    a = attrs.for_check(
        'my_team.a', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )

    # Act & Assert
    with self.assertRaisesRegex(
        TypeError, r'expected CheckWrite, got StageWrite'
    ):
      attrs.add_check_attributes(sw, a)  # type: ignore

  def test_none_check_write_target_raises_value_error(self):
    # Arrange
    a = attrs.for_check(
        'my_team.a', 'exp1', check_state_pb2.CHECK_STATE_PLANNED
    )

    # Act & Assert
    with self.assertRaisesRegex(ValueError, 'check_write cannot be None'):
      attrs.add_check_attributes(None, a)  # type: ignore

  def test_none_attribute_raises_value_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()

    # Act & Assert
    with self.assertRaisesRegex(ValueError, 'attribute cannot be None'):
      attrs.add_check_attributes(cw, None)  # type: ignore

  def test_incompatible_attribute_type_raises_type_error(self):
    # Arrange
    cw = write_nodes_request_pb2.WriteNodesRequest.CheckWrite()
    sa = attrs.for_stage(
        'my_team.stage_attr', 'exp1', stage_state_pb2.STAGE_STATE_ATTEMPTING
    )

    # Act & Assert
    with self.assertRaisesRegex(
        TypeError, r'expected CheckAttributeWrite, got StageAttributeWrite'
    ):
      attrs.add_check_attributes(cw, sa)  # type: ignore


if __name__ == '__main__':
  unittest.main()
