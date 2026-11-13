# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Inspections for graphs and roots inside TurboCI identifiers."""

from __future__ import annotations

from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils.ids import wrapping

__all__ = [
    'root',
    'same_root',
    'same_workplan',
]


def root(
    ident: wrapping.AnyIdentifier,
) -> tuple[
    identifier_pb2.WorkPlan | None,
    identifier_pb2.Check | None,
    identifier_pb2.Stage | None,
]:
  """Returns the underlying root components representing the identifier.

  Useful to inspect the baseline components (WorkPlan, Check, or Stage)
  without type switches.

  Returns:
    A 3-tuple of (WorkPlan, Check, Stage).
  """
  wp: identifier_pb2.WorkPlan | None = None
  check: identifier_pb2.Check | None = None
  stage: identifier_pb2.Stage | None = None

  match (unwrapped := wrapping.unwrap(ident)):
    case None:
      pass
    case identifier_pb2.WorkPlan():
      wp = unwrapped
    case identifier_pb2.Check():
      check = unwrapped
    case identifier_pb2.CheckResult():
      if unwrapped.HasField('check'):
        check = unwrapped.check
    case identifier_pb2.CheckEdit():
      if unwrapped.HasField('check'):
        check = unwrapped.check
    case identifier_pb2.Stage():
      stage = unwrapped
    case identifier_pb2.StageAttempt():
      if unwrapped.HasField('stage'):
        stage = unwrapped.stage
    case identifier_pb2.StageEdit():
      if unwrapped.HasField('stage'):
        stage = unwrapped.stage
    case _:
      raise NotImplementedError(f'root({type(ident)})')

  if stage is not None and stage.HasField('work_plan'):
    wp = stage.work_plan
  elif check is not None and check.HasField('work_plan'):
    wp = check.work_plan

  return wp, check, stage


def same_root(
    a: wrapping.AnyIdentifier, b: wrapping.AnyIdentifier
) -> bool:
  """Checks if two identifiers share the exact same Check or Stage root."""
  _, chk_a, stg_a = root(a)
  _, chk_b, stg_b = root(b)

  if chk_a is not None and chk_b is not None:
    return chk_a == chk_b
  if stg_a is not None and stg_b is not None:
    return stg_a == stg_b
  return False


def same_workplan(
    a: wrapping.AnyIdentifier, b: wrapping.AnyIdentifier
) -> bool:
  """Checks if two identifiers operate within the same WorkPlan context."""
  wp_a, _, _ = root(a)
  wp_b, _, _ = root(b)

  if wp_a is None or wp_b is None or not wp_a.id or not wp_b.id:
    return False
  return wp_a == wp_b
