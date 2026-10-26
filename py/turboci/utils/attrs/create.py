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

import re
from typing import cast
from typing import Sequence

from turboci.graph.orchestrator.v1 import attribute_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2
from turboci.graph.orchestrator.v1 import read_scope_pb2
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
_VALID_ATTRIBUTE_TYPES = frozenset(
    v
    for v in attribute_pb2.AttributeType.values()
    if v != attribute_pb2.ATTRIBUTE_TYPE_UNKNOWN
)


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
  if not isinstance(name, str) or not _ATTR_NAME_REGEX.match(name):
    raise ValueError(
        f'invalid attribute name {name!r}: expected dot-separated '
        "lower_snake_case with at least one dot (e.g. 'namespace.my_attr')"
    )
  for prefix in _RESERVED_PREFIXES:
    if name.startswith(prefix):
      raise ValueError(
          f'invalid attribute name {name!r}: uses reserved prefix {prefix!r}'
      )


def _resolve_attribute_type(
    attribute_type: attribute_pb2.AttributeType | str | int | None,
) -> attribute_pb2.AttributeType | None:
  """Normalizes and validates an attribute_type parameter."""
  if attribute_type is None:
    return None
  if isinstance(attribute_type, bool):
    raise TypeError(
        f'unexpected type for attribute_type: {type(attribute_type)!r}'
    )
  if isinstance(attribute_type, str):
    if attribute_type in attribute_pb2.AttributeType.keys():
      val = attribute_pb2.AttributeType.Value(attribute_type)
      if val != attribute_pb2.ATTRIBUTE_TYPE_UNKNOWN:
        return cast(attribute_pb2.AttributeType, val)
    raise ValueError(f'invalid attribute type: {attribute_type!r}')
  if isinstance(attribute_type, int):
    if attribute_type in _VALID_ATTRIBUTE_TYPES:
      return cast(attribute_pb2.AttributeType, attribute_type)
    raise ValueError(f'invalid attribute type: {attribute_type!r}')
  raise TypeError(
      f'unexpected type for attribute_type: {type(attribute_type)!r}'
  )


def _resolve_scope(
    scope: read_scope_pb2.ReadScope | str | int | None,
) -> read_scope_pb2.ReadScope | None:
  """Normalizes and validates a ReadScope parameter."""
  if scope is None:
    return None
  if isinstance(scope, str):
    if scope in read_scope_pb2.ReadScope.keys():
      scope = read_scope_pb2.ReadScope.Value(scope)
    else:
      raise ValueError(f'unknown scope name: {scope!r}')
  if isinstance(scope, bool) or not isinstance(scope, int):
    raise TypeError(f'unexpected type for scope: {type(scope)!r}')
  if scope not in read_scope_pb2.ReadScope.values():
    raise ValueError(f'unknown scope value: {scope!r}')
  return cast(read_scope_pb2.ReadScope, scope)


def _resolve_stage_state(
    on_state: stage_state_pb2.StageState | str | int | None,
) -> stage_state_pb2.StageState | None:
  """Normalizes and validates a StageState on_state parameter."""
  if on_state is None:
    return None
  if isinstance(on_state, str):
    if on_state in stage_state_pb2.StageState.keys():
      on_state = stage_state_pb2.StageState.Value(on_state)
    else:
      raise ValueError(f'unknown stage state name: {on_state!r}')
  if isinstance(on_state, bool) or not isinstance(on_state, int):
    raise TypeError(f'unexpected type for on_state: {type(on_state)!r}')
  if on_state == stage_state_pb2.STAGE_STATE_UNKNOWN:
    raise ValueError('cannot use STAGE_STATE_UNKNOWN as on_state')
  if on_state not in stage_state_pb2.StageState.values():
    raise ValueError(f'unknown stage state value: {on_state!r}')
  return cast(stage_state_pb2.StageState, on_state)


def _resolve_check_state(
    on_state: check_state_pb2.CheckState | str | int | None,
) -> check_state_pb2.CheckState | None:
  """Normalizes and validates a CheckState on_state parameter."""
  if on_state is None:
    return None
  if isinstance(on_state, str):
    if on_state in check_state_pb2.CheckState.keys():
      on_state = check_state_pb2.CheckState.Value(on_state)
    else:
      raise ValueError(f'unknown check state name: {on_state!r}')
  if isinstance(on_state, bool) or not isinstance(on_state, int):
    raise TypeError(f'unexpected type for on_state: {type(on_state)!r}')
  if on_state == check_state_pb2.CHECK_STATE_UNKNOWN:
    raise ValueError('cannot use CHECK_STATE_UNKNOWN as on_state')
  if on_state not in check_state_pb2.CheckState.values():
    raise ValueError(f'unknown check state value: {on_state!r}')
  return cast(check_state_pb2.CheckState, on_state)


def for_stage(
    name: str,
    expression: str,
    on_state: stage_state_pb2.StageState | str | int | None = None,
    attribute_type: attribute_pb2.AttributeType | str | int | None = None,
    scope: read_scope_pb2.ReadScope | str | int | None = None,
) -> write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite:
  """Creates a StageAttributeWrite for a Stage node.

  Args:
    name: Attribute name, dot-separated lower_snake_case.
    expression: CEL expression evaluated against Stage Tags.
    on_state: Optional StageState on which this attribute is evaluated.
      When omitted, left unset so the server applies STAGE_STATE_FINAL.
    attribute_type: Optional expected attribute result type.
    scope: Optional ReadScope the attribute will be visible at.

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
  resolved_scope = _resolve_scope(scope)

  return write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite(
      name=name,
      expression=expression,
      on_state=resolved_state,
      attribute_type=resolved_attr_type,
      scope=resolved_scope,
  )


def for_check(
    name: str,
    expression: str,
    on_state: check_state_pb2.CheckState | str | int | None = None,
    attribute_type: attribute_pb2.AttributeType | str | int | None = None,
    scope: read_scope_pb2.ReadScope | str | int | None = None,
) -> write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite:
  """Creates a CheckAttributeWrite for a Check node.

  Args:
    name: Attribute name, dot-separated lower_snake_case.
    expression: CEL expression evaluated against Check Tags.
    on_state: Optional CheckState on which this attribute is evaluated.
      When omitted, left unset so the server applies CHECK_STATE_FINAL.
    attribute_type: Optional expected attribute result type.
    scope: Optional ReadScope the attribute will be visible at.

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
  resolved_scope = _resolve_scope(scope)

  return write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite(
      name=name,
      expression=expression,
      on_state=resolved_state,
      attribute_type=resolved_attr_type,
      scope=resolved_scope,
  )


def add_stage_attributes(
    stage_write: write_nodes_request_pb2.WriteNodesRequest.StageWrite,
    *attrs: write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite,
) -> None:
  """Appends attributes to a StageWrite, validating uniqueness and type."""
  if stage_write is None:
    raise ValueError('stage_write cannot be None')
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
    raise ValueError('check_write cannot be None')
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
      raise ValueError(f'duplicate attribute name: {existing.name!r}')
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
      raise ValueError(f'duplicate attribute name: {attr.name!r}')
    seen.add(attr.name)
  target_container.extend(incoming_attrs)
