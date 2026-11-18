# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Constructive helpers for TurboCI AttributeWrite messages."""

from __future__ import annotations

__all__ = [
    'add_check_attributes',
    'add_stage_attributes',
    'for_check',
    'for_stage',
]

import json
import re
from typing import cast
from typing import Sequence

from turboci.graph.orchestrator.v1 import attribute_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2

_ATTR_NAME_REGEX = re.compile(
    r'^[a-z](?:[a-z0-9_]*[a-z0-9])?(?:\.[a-z](?:[a-z0-9_]*[a-z0-9])?)+$'
)
_RESERVED_PREFIXES = (
    'check.',
    'stage.',
    'work_node.',
    'worknode.',
    'work_plan.',
    'workplan.',
)


def _go_quote(s: object) -> str:
  """Quotes `s` like Go's `%q` (for the strings we accept)."""
  return json.dumps(s, ensure_ascii=False)


def _enum_label(enum_type, value: int) -> str:
  """Formats an enum value like Go's `%v`: its name, or else its number."""
  if value in enum_type.values():
    return enum_type.Name(value)
  return str(value)


def _resolve_enum(enum_type, value, unknown: int, kind: str, param: str):
  """Normalizes an enum given as a value or a name, rejecting `unknown`."""
  if isinstance(value, str):
    if value not in enum_type.keys():
      raise ValueError(f'invalid {kind}: {_go_quote(value)}')
    value = enum_type.Value(value)
  if isinstance(value, bool) or not isinstance(value, int):
    raise TypeError(f'unexpected type for {param}: {type(value)!r}')
  if value == unknown or value not in enum_type.values():
    raise ValueError(f'invalid {kind}: {_enum_label(enum_type, value)}')
  return value


def _validate_attribute_name(name: str) -> None:
  """Validates that an attribute name conforms to naming conventions.

  Attribute names must be dot-separated lower_snake_case with at least one dot
  (matching regex
  ^[a-z](?:[a-z0-9_]*[a-z0-9])?(?:\\.[a-z](?:[a-z0-9_]*[a-z0-9])?)+$) and must
  not use reserved prefixes ('check.', 'stage.', 'work_node.', 'worknode.',
  'work_plan.', 'workplan.').

  Args:
    name: The attribute name string to validate.

  Raises:
    ValueError: If the name does not match the regex or uses a reserved prefix.
  """
  if not isinstance(name, str) or not _ATTR_NAME_REGEX.fullmatch(name):
    raise ValueError(
        f'invalid attribute name {_go_quote(name)}: expected dot-separated '
        "lower_snake_case with at least one dot (e.g. 'namespace.my_attr')"
    )
  for prefix in _RESERVED_PREFIXES:
    if name.startswith(prefix):
      raise ValueError(
          f'invalid attribute name {_go_quote(name)}: uses reserved prefix '
          f'{_go_quote(prefix)}'
      )


def _resolve_attribute_type(
    attribute_type: attribute_pb2.AttributeType | str | int | None,
) -> attribute_pb2.AttributeType | None:
  """Normalizes and validates an attribute_type parameter."""
  if attribute_type is None:
    return None
  return cast(
      attribute_pb2.AttributeType,
      _resolve_enum(
          attribute_pb2.AttributeType,
          attribute_type,
          attribute_pb2.ATTRIBUTE_TYPE_UNKNOWN,
          'attribute type',
          'attribute_type',
      ),
  )


def _resolve_stage_state(
    on_state: stage_state_pb2.StageState | str | int | None,
) -> stage_state_pb2.StageState | None:
  """Normalizes and validates a StageState on_state parameter."""
  if on_state is None:
    return None
  return cast(
      stage_state_pb2.StageState,
      _resolve_enum(
          stage_state_pb2.StageState,
          on_state,
          stage_state_pb2.STAGE_STATE_UNKNOWN,
          'stage state',
          'on_state',
      ),
  )


def _resolve_check_state(
    on_state: check_state_pb2.CheckState | str | int | None,
) -> check_state_pb2.CheckState | None:
  """Normalizes and validates a CheckState on_state parameter."""
  if on_state is None:
    return None
  return cast(
      check_state_pb2.CheckState,
      _resolve_enum(
          check_state_pb2.CheckState,
          on_state,
          check_state_pb2.CHECK_STATE_UNKNOWN,
          'check state',
          'on_state',
      ),
  )


def for_stage(
    name: str,
    expression: str,
    on_state: stage_state_pb2.StageState | str | int | None = None,
    attribute_type: attribute_pb2.AttributeType | str | int | None = None,
    indexed: bool | None = None,
) -> write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite:
  """Creates a StageAttributeWrite for a Stage node.

  Args:
    name: Attribute name, dot-separated lower_snake_case.
    expression: CEL expression evaluated against Stage Tags.
    on_state: Optional StageState on which this attribute is evaluated.
      When omitted, left unset so the server applies STAGE_STATE_FINAL.
    attribute_type: Optional expected attribute result type.
    indexed: Whether this attribute should be exposed in search indexes.
      When omitted, left unset.

  Returns:
    StageAttributeWrite configured with on_state.

  Raises:
    ValueError: If name, expression, on_state, or attribute_type is invalid.
    TypeError: If on_state or attribute_type has an invalid type.
  """
  _validate_attribute_name(name)
  if not expression:
    raise ValueError('expression cannot be empty')
  resolved_state = _resolve_stage_state(on_state)
  resolved_attr_type = _resolve_attribute_type(attribute_type)

  return write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite(
      name=name,
      expression=expression,
      on_state=resolved_state,
      attribute_type=resolved_attr_type,
      indexed=indexed,
  )


def for_check(
    name: str,
    expression: str,
    on_state: check_state_pb2.CheckState | str | int | None = None,
    attribute_type: attribute_pb2.AttributeType | str | int | None = None,
    indexed: bool | None = None,
) -> write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite:
  """Creates a CheckAttributeWrite for a Check node.

  Args:
    name: Attribute name, dot-separated lower_snake_case.
    expression: CEL expression evaluated against Check Tags.
    on_state: Optional CheckState on which this attribute is evaluated.
      When omitted, left unset so the server applies CHECK_STATE_FINAL.
    attribute_type: Optional expected attribute result type.
    indexed: Whether this attribute should be exposed in search indexes.
      When omitted, left unset.

  Returns:
    CheckAttributeWrite configured with on_state.

  Raises:
    ValueError: If name, expression, on_state, or attribute_type is invalid.
    TypeError: If on_state or attribute_type has an invalid type.
  """
  _validate_attribute_name(name)
  if not expression:
    raise ValueError('expression cannot be empty')
  resolved_state = _resolve_check_state(on_state)
  resolved_attr_type = _resolve_attribute_type(attribute_type)

  return write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite(
      name=name,
      expression=expression,
      on_state=resolved_state,
      attribute_type=resolved_attr_type,
      indexed=indexed,
  )


def add_stage_attributes(
    stage_write: write_nodes_request_pb2.WriteNodesRequest.StageWrite,
    *attrs: write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite,
) -> None:
  """Appends attributes to a StageWrite, validating uniqueness and type."""
  if stage_write is None:
    raise ValueError('stage write cannot be None')
  if not isinstance(
      stage_write, write_nodes_request_pb2.WriteNodesRequest.StageWrite
  ):
    raise TypeError(f'expected StageWrite, got {type(stage_write).__name__}')
  _validate_and_append_attributes(
      target_container=stage_write.attributes,
      expected_type=(
          write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite
      ),
      incoming_attrs=attrs,
  )


def add_check_attributes(
    check_write: write_nodes_request_pb2.WriteNodesRequest.CheckWrite,
    *attrs: write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite,
) -> None:
  """Appends attributes to a CheckWrite, validating uniqueness and type."""
  if check_write is None:
    raise ValueError('check write cannot be None')
  if not isinstance(
      check_write, write_nodes_request_pb2.WriteNodesRequest.CheckWrite
  ):
    raise TypeError(f'expected CheckWrite, got {type(check_write).__name__}')
  _validate_and_append_attributes(
      target_container=check_write.attributes,
      expected_type=(
          write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite
      ),
      incoming_attrs=attrs,
  )


def _validate_and_append_attributes(
    target_container,
    expected_type: type,
    incoming_attrs: Sequence[object],
) -> None:
  seen: set[str] = set()
  for existing in target_container:
    if existing.name in seen:
      raise ValueError(
          f'duplicate attribute name {_go_quote(existing.name)}'
      )
    seen.add(existing.name)
  for attr in incoming_attrs:
    if attr is None:
      raise ValueError('attribute cannot be None')
    if not isinstance(attr, expected_type):
      raise TypeError(
          f'expected {expected_type.__name__}, got {type(attr).__name__}'
      )
    _validate_attribute_name(attr.name)
    if attr.name in seen:
      raise ValueError(f'duplicate attribute name {_go_quote(attr.name)}')
    seen.add(attr.name)
  target_container.extend(incoming_attrs)
