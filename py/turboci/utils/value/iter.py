# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Helpers for iterating through the ValueRefs of TurboCI messages."""

from __future__ import annotations

import dataclasses
import typing

from turboci.graph.ids.v1 import identifier_pb2
from turboci.graph.orchestrator.v1 import actor_pb2
from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import edit_pb2
from turboci.graph.orchestrator.v1 import stage_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2
from turboci.utils import ids

__all__ = [
    'CommonRefContext',
    'RefContext',
    'ResultDataRefContext',
    'refs_in',
]


@dataclasses.dataclass(frozen=True)
class CommonRefContext:
  """Context yielded by `refs_in` for all ValueSlots other than VALUE_SLOT_CHECK_RESULT_DATA."""

  slot: value_slot_pb2.ValueSlot
  id: identifier_pb2.Identifier | None = None


@dataclasses.dataclass(frozen=True)
class ResultDataRefContext(CommonRefContext):
  """Context yielded by `refs_in` for ValueRefs in Check.results data (VALUE_SLOT_CHECK_RESULT_DATA)."""

  # 0-based index of the Check.Result in Check.results in which the ValueRef
  # was found.
  idx: int = 0
  # Owner of the Check.Result.
  actor: actor_pb2.Actor | None = None


RefContext = CommonRefContext | ResultDataRefContext


def refs_in(
    obj: (
        stage_pb2.Stage
        | stage_pb2.Stage.Attempt
        | check_pb2.Check
        | workplan_pb2.WorkPlan
        | edit_pb2.Edit
        | typing.Any
    ),
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  """Returns an iterator over all ValueRefs in `obj`.

  For Check objects (including Checks within a WorkPlan), Check.results data
  (VALUE_SLOT_CHECK_RESULT_DATA) is yielded in reverse Check.results order with
  a ResultDataRefContext so the latest version of results is available first.
  All other ValueSlots are yielded with a CommonRefContext.

  Args:
    obj: A Stage, Stage.Attempt, Check, WorkPlan, or Edit proto message.

  Returns:
    An iterator yielding `(RefContext, ValueRef)` pairs.

  Raises:
    ValueError: If `obj` is not a supported message type or contains an
      invalid Edit.
  """
  match obj:
    case stage_pb2.Stage():
      return _refs_in_stage(obj)
    case stage_pb2.Stage.Attempt():
      return _refs_in_stage_attempt(obj)
    case check_pb2.Check():
      return _refs_in_check(obj)
    case workplan_pb2.WorkPlan():
      return _refs_in_workplan(obj)
    case edit_pb2.Edit():
      return _refs_in_edit(obj)
    case _:
      raise ValueError(f'impossible: bad type {type(obj).__name__}')


def _refs_in_stage(
    stage: stage_pb2.Stage,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  stage_id = (
      ids.wrap(stage.identifier) if stage.HasField('identifier') else None
  )
  if stage.HasField('args'):
    yield (
        CommonRefContext(
            slot=value_slot_pb2.VALUE_SLOT_STAGE_ARGS,
            id=stage_id,
        ),
        stage.args,
    )

  if stage.HasField('legacy') and stage.legacy.HasField('worknode'):
    yield (
        CommonRefContext(
            slot=value_slot_pb2.VALUE_SLOT_STAGE_LEGACY_WORKNODE,
            id=stage_id,
        ),
        stage.legacy.worknode,
    )

  for edit in stage.edits:
    yield from _refs_in_stage_edit(edit)

  for attempt in stage.attempts:
    yield from _refs_in_stage_attempt(attempt)


def _refs_in_stage_attempt(
    attempt: stage_pb2.Stage.Attempt,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  attempt_id = (
      ids.wrap(attempt.identifier) if attempt.HasField('identifier') else None
  )
  for detail in attempt.details:
    yield (
        CommonRefContext(
            slot=value_slot_pb2.VALUE_SLOT_ATTEMPT_DETAIL,
            id=attempt_id,
        ),
        detail,
    )

  for progress in attempt.progress:
    for detail in progress.details:
      yield (
          CommonRefContext(
              slot=value_slot_pb2.VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL,
              id=attempt_id,
          ),
          detail,
      )


def _stage_edit_id(edit: edit_pb2.Edit) -> identifier_pb2.Identifier | None:
  stg = (
      edit.for_node.stage
      if edit.HasField('for_node') and edit.for_node.HasField('stage')
      else None
  )
  ver = (
      edit.version.ts
      if edit.HasField('version') and edit.version.HasField('ts')
      else None
  )
  if stg is None and ver is None:
    return None
  return ids.wrap(identifier_pb2.StageEdit(stage=stg, version=ver))


def _check_edit_id(edit: edit_pb2.Edit) -> identifier_pb2.Identifier | None:
  chk = (
      edit.for_node.check
      if edit.HasField('for_node') and edit.for_node.HasField('check')
      else None
  )
  ver = (
      edit.version.ts
      if edit.HasField('version') and edit.version.HasField('ts')
      else None
  )
  if chk is None and ver is None:
    return None
  return ids.wrap(identifier_pb2.CheckEdit(check=chk, version=ver))


def _refs_in_stage_edit(
    edit: edit_pb2.Edit,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  if edit.HasField('check') or (
      edit.HasField('for_node') and edit.for_node.HasField('check')
  ):
    raise ValueError('impossible: Check edit in Stage')

  def _gen() -> typing.Iterator[tuple[RefContext, value_ref_pb2.ValueRef]]:
    edit_id = _stage_edit_id(edit)
    for detail in edit.reason.details:
      yield (
          CommonRefContext(
              slot=value_slot_pb2.VALUE_SLOT_STAGE_EDIT_REASON_DETAIL,
              id=edit_id,
          ),
          detail,
      )

    for attempt in edit.stage.attempts:
      attempt_id = (
          ids.wrap(attempt.identifier)
          if attempt.HasField('identifier')
          else None
      )
      for detail in attempt.details:
        yield (
            CommonRefContext(
                slot=value_slot_pb2.VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL,
                id=attempt_id,
            ),
            detail,
        )

  return _gen()


def _refs_in_check_edit(
    edit: edit_pb2.Edit,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  if edit.HasField('stage') or (
      edit.HasField('for_node') and edit.for_node.HasField('stage')
  ):
    raise ValueError('impossible: Stage edit in Check')

  def _gen() -> typing.Iterator[tuple[RefContext, value_ref_pb2.ValueRef]]:
    edit_id = _check_edit_id(edit)
    for detail in edit.reason.details:
      yield (
          CommonRefContext(
              slot=value_slot_pb2.VALUE_SLOT_CHECK_EDIT_REASON_DETAIL,
              id=edit_id,
          ),
          detail,
      )

    for option in edit.check.options:
      yield (
          CommonRefContext(
              slot=value_slot_pb2.VALUE_SLOT_CHECK_EDIT_OPTION,
              id=edit_id,
          ),
          option,
      )

    for result in edit.check.results:
      result_id = (
          ids.wrap(result.identifier)
          if result.HasField('identifier')
          else None
      )
      for dat in result.data:
        yield (
            CommonRefContext(
                slot=value_slot_pb2.VALUE_SLOT_CHECK_EDIT_RESULT_DATA,
                id=result_id,
            ),
            dat,
        )

  return _gen()


def _refs_in_edit(
    edit: edit_pb2.Edit,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  match edit.WhichOneof('delta'):
    case 'stage':
      return _refs_in_stage_edit(edit)
    case 'check':
      return _refs_in_check_edit(edit)

  if edit.HasField('for_node'):
    match edit.for_node.WhichOneof('type'):
      case 'stage':
        return _refs_in_stage_edit(edit)
      case 'check':
        return _refs_in_check_edit(edit)

  raise ValueError(
      'impossible: Edit must have stage or check delta or for_node set'
  )


def _refs_in_check(
    check: check_pb2.Check,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  check_id = (
      ids.wrap(check.identifier) if check.HasField('identifier') else None
  )
  for option in check.options:
    yield (
        CommonRefContext(
            slot=value_slot_pb2.VALUE_SLOT_CHECK_OPTION,
            id=check_id,
        ),
        option,
    )

  for i in range(len(check.results) - 1, -1, -1):
    r = check.results[i]
    ctx = ResultDataRefContext(
        slot=value_slot_pb2.VALUE_SLOT_CHECK_RESULT_DATA,
        id=ids.wrap(r.identifier) if r.HasField('identifier') else None,
        idx=i,
        actor=r.owner if r.HasField('owner') else None,
    )
    for dat in r.data:
      yield ctx, dat

  for edit in check.edits:
    yield from _refs_in_check_edit(edit)


def _refs_in_workplan(
    wp: workplan_pb2.WorkPlan,
) -> typing.Iterable[tuple[RefContext, value_ref_pb2.ValueRef]]:
  for stage in wp.stages:
    yield from _refs_in_stage(stage)

  for check in wp.checks:
    yield from _refs_in_check(check)
