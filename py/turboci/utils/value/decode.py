# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines OmittedDataError, decode, decode_data, get_data, lookup and results."""

from __future__ import annotations

__all__ = [
    'OmittedDataError',
    'decode',
    'decode_data',
    'get_data',
    'lookup',
    'results',
]


import typing

from google.protobuf import json_format
from google.protobuf import message

from turboci.graph.orchestrator.v1 import check_pb2
from turboci.graph.orchestrator.v1 import omit_reason_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.utils import value
from turboci.utils.value import data_source
from turboci.utils.value import ordered

T = typing.TypeVar('T', bound=message.Message)


class OmittedDataError(ValueError):
  """Raised when attempting to read or copy data from an omitted ValueRef."""

  omit_reason: omit_reason_pb2.OmitReason

  def __init__(
      self,
      omit_reason: omit_reason_pb2.OmitReason,
      prefix: str = '',
  ) -> None:
    self.omit_reason = omit_reason
    try:
      reason_name = omit_reason_pb2.OmitReason.Name(omit_reason)
    except ValueError:
      reason_name = str(int(omit_reason))
    msg = f'data is omitted: {reason_name}'
    if prefix:
      msg = f'{prefix}: {msg}'
    super().__init__(msg)


def decode(
    ds: data_source.DataSource, ref: value_ref_pb2.ValueRef, msg: type[T]
) -> T:
  """Decodes and returns a proto of type `msg` from the given ValueRef.

  Args:
    ds: A DataSource used to pull ValueData by digest.
    ref: The ValueRef to decode.
    msg: The expected message type to decode.

  Returns:
    The decoded message of type `msg`, or None if `ref`'s data is not present in
    `ds`.

  Raises:
    OmittedDataError: If `ref` has `omit_reason` set.
    ValueError: If the type of the ref does not match the type of `msg`.
    message.DecodeError: If the data cannot be decoded.
  """
  if ref.type_url != (targ_url := value.url(msg)):
    raise ValueError(f'mismatched types "{targ_url}" != "{ref.type_url}"')

  return decode_data(get_data(ds, ref), msg)


def decode_data(data: None | value_data_pb2.ValueData, msg: type[T]) -> T:
  """Decodes and returns a proto of type `msg` from the given ValueData.

  Args:
    data: The ValueData to decode, or None.
    msg: The expected message type to decode.

  Returns:
    The decoded message of type `msg`, or None if `data` is None or has neither
    binary nor json populated.

  Raises:
    ValueError: If data is None, or empty.
    message.DecodeError: If the ValueData has a type_url mismatch or cannot be
      decoded.
  """
  if data is None:
    raise ValueError('data is None')

  which = data.WhichOneof('data')
  if which is None:
    raise ValueError('data is empty')

  targ_url = value.url(msg)
  if which == 'binary':
    bin_data = data.binary
    if bin_data.type_url != targ_url:
      raise message.DecodeError(
          f'BUG: mismatched types "{targ_url}" != "{bin_data.type_url}" in'
          ' ValueData'
      )
    ret = msg()
    try:
      if not bin_data.Unpack(ret):
        raise message.DecodeError(f'failed to unpack "{targ_url}"')
    except message.DecodeError as ex:
      raise message.DecodeError(
          f'failed to unmarshal binary for "{targ_url}": {ex}'
      ) from ex
    return ret

  json_data = data.json
  if json_data.type_url != targ_url:
    raise message.DecodeError(
        f'BUG: mismatched types "{targ_url}" != "{json_data.type_url}" in'
        ' ValueData'
    )

  ret = msg()
  try:
    json_format.Parse(json_data.value, ret, ignore_unknown_fields=True)
  except json_format.ParseError as ex:
    raise message.DecodeError(
        f'failed to parse JSON for "{targ_url}": {ex}'
    ) from ex
  return ret


def lookup(
    ds: data_source.DataSource,
    refs: typing.Sequence[value_ref_pb2.ValueRef],
    msg: type[T],
) -> None | T:
  """Finds and decodes the first non-omitted ValueRef of type `T`.

  ValueRefs sorted by type_url.

  Note that ValueRefs do not need to be unique by type_url (such as for
  edit reason details).

  This assumes that `set` is sorted by "type_url" and will do a binary search.

  Args:
    ds: A DataSource used to pull ValueData by digest.
    refs: Sequence of ValueRef, sorted by type_url.
    msg: The type of ValueRef to find.

  Returns:
    The found and decoded ref or None, if no non-omitted refs matched.
  """
  val = ordered.find(refs, value.url(msg))
  if val:
    return decode(ds, val, msg)
  return None


def results(
    ds: data_source.DataSource,
    check: check_pb2.Check,
    msg: type[T],
) -> list[T]:
  """Collects all result data from the Check of type T.

  Args:
    ds: A DataSource used to pull ValueData by digest.
    refs: Sequence of ValueRef, sorted by type_url.
    msg: The type of ValueRef to find.

  Returns:
    All non-omitted result data in this Check which match `msg` (which may be
    none).
  """
  ret: list[T] = []
  for rslt in check.results:
    if (x := lookup(ds, rslt.data, msg)) is not None:
      ret.append(x)
  return ret


def get_data(
    ds: data_source.DataSource, ref: value_ref_pb2.ValueRef
) -> None | value_data_pb2.ValueData:
  """Gets the raw ValueData for the given ref.

  Synthesizes a new ValueData if `ref` contains inline data.

  Args:
    ds: A DataSource used to pull ValueData by digest.
    ref: The ValueRef to retrieve data for.

  Returns:
    The ValueData for `ref`, or None if `ref` is not present in `ds`.

  Raises:
    OmittedDataError: If `ref` has `omit_reason` set.
  """
  if ref.HasField('omit_reason'):
    raise OmittedDataError(ref.omit_reason)

  if ref.HasField('inline'):
    return value_data_pb2.ValueData(binary=ref.inline)

  if ref.HasField('digest'):
    return ds.get(ref.digest)

  return None
