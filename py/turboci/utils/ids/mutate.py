# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Provides helpers to mutate identifiers, e.g. binding them to a workplan."""

from __future__ import annotations

import typing

from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils.ids.create import _normalize_workplan
from turboci.utils.ids.wrap import AnyIdentifier, unwrap

__all__ = [
    'set_workplan',
    'clear_workplan',
]


SpecificIdent = typing.TypeVar('SpecificIdent', bound=AnyIdentifier)


def set_workplan(
    ident: SpecificIdent, workplan_id: str | int | identifier_pb2.WorkPlan
) -> SpecificIdent:
  """Sets or overrides the bound WorkPlan on an identifier.

  Args:
    ident: The target identifier to mutate.
    workplan_id: The targeted workplan ID (with or without 'L' prefix) or int or
      identifier_pb2.WorkPlan.

  Returns:
    The modified identifier with the bound workplan.
  """
  wp_cleaned = _normalize_workplan(workplan_id)

  match (unwrapped := unwrap(ident)):
    case identifier_pb2.WorkPlan():
      unwrapped.id = wp_cleaned
    case identifier_pb2.Check():
      unwrapped.work_plan.id = wp_cleaned
    case identifier_pb2.CheckResult():
      unwrapped.check.work_plan.id = wp_cleaned
    case identifier_pb2.CheckEdit():
      unwrapped.check.work_plan.id = wp_cleaned
    case identifier_pb2.Stage():
      unwrapped.work_plan.id = wp_cleaned
    case identifier_pb2.StageAttempt():
      unwrapped.stage.work_plan.id = wp_cleaned
    case identifier_pb2.StageEdit():
      unwrapped.stage.work_plan.id = wp_cleaned
    case _:
      raise NotImplementedError(f'set_workplan({type(ident)})')

  return ident


def clear_workplan(ident: SpecificIdent) -> SpecificIdent:
  """Clear workplan removes the workplan portion of an identifier.

  Raises NotImplementedError if `ident` is, itself, a WorkPlan.

  Returns:
    The modified identifier with the workplan removed.
  """
  match (unwrapped := unwrap(ident)):
    case identifier_pb2.Check():
      unwrapped.ClearField('work_plan')
    case identifier_pb2.CheckResult():
      unwrapped.check.ClearField('work_plan')
    case identifier_pb2.CheckEdit():
      unwrapped.check.ClearField('work_plan')
    case identifier_pb2.Stage():
      unwrapped.ClearField('work_plan')
    case identifier_pb2.StageAttempt():
      unwrapped.stage.ClearField('work_plan')
    case identifier_pb2.StageEdit():
      unwrapped.stage.ClearField('work_plan')
    case _:
      raise NotImplementedError(f'clear_workplan({type(ident)})')

  return ident
