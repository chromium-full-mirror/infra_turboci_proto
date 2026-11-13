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

from collections import abc
import json
import typing

from google.protobuf import timestamp_pb2

from turboci.graph.ids.v1 import identifier_pb2
from turboci.utils.ids import wrapping

_T = typing.TypeVar('_T', bound=wrapping.SpecificIdentifier)
_IdentParser: typing.TypeAlias = abc.Callable[
    [list[str]], wrapping.SpecificIdentifier | None
]


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


def _require_non_empty(trimmed: str) -> str:
  if not trimmed:
    raise ValueError('unexpected empty token')
  return trimmed


def _require_int(trimmed: str) -> int:
  try:
    ret = int(trimmed, 10)
  except ValueError as ex:
    raise ValueError(f'bad idx {json.dumps(trimmed)}: {ex}') from ex
  if ret > 2**31 - 1 or ret < -(2**31):
    raise ValueError(
        f'bad idx {json.dumps(trimmed)}: value out of int32 range'
    )
  if ret <= 0:
    raise ValueError(f'bad idx {json.dumps(trimmed)}: must be > 0')
  return ret


def _require_ts(trimmed: str) -> timestamp_pb2.Timestamp:
  parts = trimmed.split('/')
  if len(parts) != 2:
    raise ValueError('bad timestamp: needed seconds/nanos')
  try:
    seconds = int(parts[0], 10)
  except ValueError as ex:
    raise ValueError(
        f'bad timestamp: parsing seconds {json.dumps(parts[0])}: {ex}'
    ) from ex
  if seconds > 2**63 - 1 or seconds < -(2**63):
    raise ValueError(
        f'bad timestamp: parsing seconds {json.dumps(parts[0])}: '
        'value out of int64 range'
    )
  try:
    nanos = int(parts[1], 10)
  except ValueError as ex:
    raise ValueError(
        f'bad timestamp: parsing nanos {json.dumps(parts[1])}: {ex}'
    ) from ex
  if nanos > 2**31 - 1 or nanos < -(2**31):
    raise ValueError(
        f'bad timestamp: parsing nanos {json.dumps(parts[1])}: '
        'value out of int32 range'
    )
  return timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)


def _optional_ident(
    key: str,
    toks: list[str],
    want_cls: type[_T],
) -> _T | None:
  msg = _KEY_TO_IDENT[key](toks)
  if msg is None:
    return None
  if not isinstance(msg, want_cls):
    raise ValueError(
        f'expected "{want_cls.DESCRIPTOR.name}", got "{msg.DESCRIPTOR.name}"'
    )
  return msg


def _require_ident(
    key: str,
    toks: list[str],
    want_cls: type[_T],
) -> _T:
  msg = _optional_ident(key, toks, want_cls)
  if msg is None:
    raise ValueError(f'missing required "{want_cls.DESCRIPTOR.name}"')
  return msg


def _stage_with_worknode(
    toks: list[str], is_worknode: bool
) -> identifier_pb2.Stage:
  stg = _require_ident('L?', toks, identifier_pb2.Stage)
  stg.is_worknode = is_worknode
  return stg


_KEY_TO_IDENT: dict[str, _IdentParser] = {
    'L': lambda toks: (
        identifier_pb2.WorkPlan(id=toks[0]) if toks[0] else None
    ),
    'LC': lambda toks: identifier_pb2.Check(
        work_plan=_optional_ident('L', toks, identifier_pb2.WorkPlan),
        id=_require_non_empty(toks[1]),
    ),
    'LCR': lambda toks: identifier_pb2.CheckResult(
        check=_require_ident('LC', toks, identifier_pb2.Check),
        idx=_require_int(toks[2]),
    ),
    'LCV': lambda toks: identifier_pb2.CheckEdit(
        check=_require_ident('LC', toks, identifier_pb2.Check),
        version=_require_ts(toks[2]),
    ),
    'L?': lambda toks: identifier_pb2.Stage(
        work_plan=_optional_ident('L', toks, identifier_pb2.WorkPlan),
        id=_require_non_empty(toks[1]),
    ),
    'LS': lambda toks: _stage_with_worknode(toks, False),
    'LN': lambda toks: _stage_with_worknode(toks, True),
    'L?A': lambda toks: identifier_pb2.StageAttempt(
        stage=_require_ident('L?', toks, identifier_pb2.Stage),
        idx=_require_int(toks[2]),
    ),
    'LSA': lambda toks: identifier_pb2.StageAttempt(
        stage=_require_ident('LS', toks, identifier_pb2.Stage),
        idx=_require_int(toks[2]),
    ),
    'LNA': lambda toks: identifier_pb2.StageAttempt(
        stage=_require_ident('LN', toks, identifier_pb2.Stage),
        idx=_require_int(toks[2]),
    ),
    'L?V': lambda toks: identifier_pb2.StageEdit(
        stage=_require_ident('L?', toks, identifier_pb2.Stage),
        version=_require_ts(toks[2]),
    ),
    'LSV': lambda toks: identifier_pb2.StageEdit(
        stage=_require_ident('LS', toks, identifier_pb2.Stage),
        version=_require_ts(toks[2]),
    ),
    'LNV': lambda toks: identifier_pb2.StageEdit(
        stage=_require_ident('LN', toks, identifier_pb2.Stage),
        version=_require_ts(toks[2]),
    ),
}


def from_string(ident_str: str) -> identifier_pb2.Identifier:
  """Converts from a canonical string identifier to a wrapped Identifier."""
  toks = ident_str.split(':')

  key_chars: list[str] = []
  for i, tok in enumerate(toks):
    if not tok:
      if i == 0 and len(toks) > 1:
        # workplan allowed to be empty
        key_chars.append('L')
      else:
        raise ValueError(f'in {json.dumps(ident_str)}: token {i} was empty?')
    elif i == 0 and tok == 'L':
      raise ValueError(f'in {json.dumps(ident_str)}: unexpected empty token')
    else:
      key_chars.append(tok[0])
      toks[i] = tok[1:]

  key = ''.join(key_chars)
  fn = _KEY_TO_IDENT.get(key)
  if fn is None:
    raise ValueError(
        f'in {json.dumps(ident_str)}: unexpected key {json.dumps(key)}'
    )

  try:
    ret = fn(toks)
  except ValueError as ex:
    raise ValueError(f'in {json.dumps(ident_str)}: {ex}') from ex

  if ret is None:
    raise AssertionError('unreachable: parsed empty identifier')
  return wrapping.wrap(ret)
