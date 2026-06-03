# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines DataSource and SimpleDataSource types and helpers."""

from __future__ import annotations

__all__ = [
    'DataSource',
    'MutableDataSource',
    'SimpleDataSource',
    'pick_data',
]

import collections
import typing

from turboci.graph.orchestrator.v1 import value_data_pb2


@typing.runtime_checkable
class DataSource(typing.Protocol):
  """Type definition used by reader/decoder functions in the value module.

  In particular, this is a subset of `Mapping[str, ValueData]`.
  """

  def __getitem__(self, key: str, /) -> value_data_pb2.ValueData:
    ...

  def keys(self) -> typing.Iterable[str]:
    ...


# Type definition for a mutable DataSource.
MutableDataSource = typing.MutableMapping[str, value_data_pb2.ValueData]


class SimpleDataSource(
    collections.UserDict[str, value_data_pb2.ValueData], MutableDataSource
):
  """A implementation of DataSource which uses `pick_data` to apply updates.

  Keys in this are `str`, but can be trivially cast to Digest.

  Assignment to this map uses `pick_data` to incorporate the assigned data
  instead of simple overwrites.

  If you plan on keeping a DataSource around between multiple calls, consider
  using this to minimize memory usage for overlapping data returned from
  multiple TurboCI RPCs.
  """

  def __setitem__(self, key: str, data: value_data_pb2.ValueData):
    """Incorporates `data` @ `key` into this SimpleDataSource.

    Uses `pick_data` to compute merged value.

    Args:
      key: The digest to update.
      data: The data to incorporate.
    """
    super().__setitem__(key, pick_data(self.get(key), data))


def pick_data(
    a: None | value_data_pb2.ValueData, b: value_data_pb2.ValueData
) -> value_data_pb2.ValueData:
  """Returns either `a` or `b` depending on which is better.

  Both `a` and `b` must be well-formed (one of `binary` or `json` must be
  populated)

  Prefers JSON without unknown fields to JSON with unknown fields.
  Prefers JSON to binary data.
  Prefers binary data with conversion_failure enum to binary data without.

  Args:
    a: The left-hand-side ValueData (or None, if there is no current ValueData)
    b: The right-hand-side ValueData.

  Returns:
    The selected ValueData.
  """
  if not a:
    return b

  a_binary, a_json = a.HasField('binary'), a.HasField('json')
  b_binary, b_json = b.HasField('binary'), b.HasField('json')

  if a_binary and b_json:
    return b

  if a_json and b_binary:
    if a.json.has_unknown_fields and not b.json.has_unknown_fields:
      return b
    return a

  if a_json and not b_json:
    return a

  if not a.conversion_failure and b.conversion_failure:
    return b

  return a
