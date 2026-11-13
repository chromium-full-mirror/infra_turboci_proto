# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines parsing and string serialization for TurboCI identifiers."""

from __future__ import annotations

__all__ = [
    'InvalidIdentifierError',
    'from_string',
    'to_string',
    'to_string_err',
]

from google.protobuf import timestamp_pb2

from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils.ids import wrapping


class InvalidIdentifierError(ValueError):
  """Raised by `to_string_err` when given an invalid identifier."""

  def __init__(self, reason: str) -> None:
    super().__init__(f'turboci invalid identifier: {reason}')


def to_string_err(ident: wrapping.AnyIdentifier) -> str:
  """Converts from a proto identifier to a canonical string.

  For stages without `is_worknode` set, this will generate string IDs like:

    L123456789:?stage id

  These IDs are not valid for reading or writing to the graph, but are a useful
  intermediate/local representation for stages whose worknode-ness is unknown.

  Raises:
    InvalidIdentifierError: If `ident` is unset or empty. For logging/display
      purposes, consider `to_string` instead which renders all such errors as
      `f'<{err}>'`.
  """

  def fmt_rev(ts: timestamp_pb2.Timestamp) -> str:
    return f'{ts.seconds}/{ts.nanos}'

  any_id = wrapping.unwrap(ident)
  if any_id is None:
    raise InvalidIdentifierError('id could not be unwrapped')

  parts: list[str] = []
  stop = False

  while not stop:
    match any_id:
      case identifier_pb2.WorkPlan():
        if any_id.id:
          parts.append(f'L{any_id.id}')
        stop = True

      case identifier_pb2.Check():
        parts.extend([f'{any_id.id}', ':C'])
        any_id = any_id.work_plan

      case identifier_pb2.CheckResult():
        parts.extend([f'{any_id.idx}', ':R'])
        any_id = any_id.check

      case identifier_pb2.CheckEdit():
        parts.extend([f'{fmt_rev(any_id.version)}', ':V'])
        any_id = any_id.check

      case identifier_pb2.Stage():
        pfx = ':?'
        if any_id.HasField('is_worknode'):
          pfx = ':N' if any_id.is_worknode else ':S'

        parts.extend([f'{any_id.id}', pfx])
        any_id = any_id.work_plan

      case identifier_pb2.StageAttempt():
        parts.extend([f'{any_id.idx}', ':A'])
        any_id = any_id.stage

      case identifier_pb2.StageEdit():
        parts.extend([f'{fmt_rev(any_id.version)}', ':V'])
        any_id = any_id.stage

      case _:
        raise NotImplementedError(f'to_string_err({type(ident)})')

  if not parts:
    raise InvalidIdentifierError('id was empty')

  parts.reverse()
  return ''.join(parts)


def to_string(ident: wrapping.AnyIdentifier) -> str:
  """Error-less counterpart of `to_string_err`.

  Renders all `InvalidIdentifierError` exceptions as `f'<{err}>'`.
  """
  try:
    return to_string_err(ident)
  except InvalidIdentifierError as err:
    return f'<{err}>'


def from_string(ident_str: str) -> identifier_pb2.Identifier:
  """Converts from a canonical string identifier to a wrapped Identifier."""
  toks = ident_str.split(':')
  for i, t in enumerate(toks):
    if i > 0 and not t:
      raise ValueError(f'from_string: empty token {i} in {ident_str!r}')

  # trim are the tokens with the leading char removed
  trim = [t[1:] for t in toks]
  ret = identifier_pb2.Identifier()

  def non_empty(v: str) -> str:
    if not v:
      raise ValueError(f'from_string: unexpected empty token in {ident_str!r}')
    return v

  def set_wp(wp: identifier_pb2.WorkPlan) -> None:
    if toks[0]:
      wp.id = non_empty(trim[0])

  def parse_is_worknode(stg: identifier_pb2.Stage) -> None:
    """Parses toks[1][0] for S, N, ?"""
    match toks[1][0]:
      case 'N':
        stg.is_worknode = True
      case 'S':
        stg.is_worknode = False
      case '?':
        stg.ClearField('is_worknode')
      case _:
        raise ValueError(
            'from_string: expected token to start with S, N or ?, '
            f'got {toks[1][0]!r}'
        )

  def parse_idx(v: str) -> int:
    idx = int(v)
    if idx <= 0:
      raise ValueError(f'from_string: idx must be > 0, got {idx}')
    return idx

  def parse_vers(v: str, to: timestamp_pb2.Timestamp) -> None:
    secs, nanos = v.split('/')
    to.seconds = int(secs)
    to.nanos = int(nanos)

  match [t[0] if t else '' for t in toks]:
    case ['L' | '']:
      set_wp(ret.work_plan)

    case ['L' | '', 'C']:
      set_wp(ret.check.work_plan)
      ret.check.id = non_empty(trim[1])

    case ['L' | '', 'C', 'R']:
      set_wp(ret.check_result.check.work_plan)
      ret.check_result.check.id = non_empty(trim[1])
      ret.check_result.idx = parse_idx(trim[2])

    case ['L' | '', 'C', 'V']:
      set_wp(ret.check_edit.check.work_plan)
      ret.check_edit.check.id = non_empty(trim[1])
      parse_vers(trim[2], ret.check_edit.version)

    case ['L' | '', _]:
      set_wp(ret.stage.work_plan)
      parse_is_worknode(ret.stage)
      ret.stage.id = non_empty(trim[1])

    case ['L' | '', _, 'A']:
      set_wp(ret.stage_attempt.stage.work_plan)
      parse_is_worknode(ret.stage_attempt.stage)
      ret.stage_attempt.stage.id = non_empty(trim[1])
      ret.stage_attempt.idx = parse_idx(trim[2])

    case ['L' | '', _, 'V']:
      set_wp(ret.stage_edit.stage.work_plan)
      parse_is_worknode(ret.stage_edit.stage)
      ret.stage_edit.stage.id = non_empty(trim[1])
      parse_vers(trim[2], ret.stage_edit.version)

  if not ret.WhichOneof('type'):
    raise ValueError(f'from_string: unrecognized ID {ident_str!r}')

  return ret
