# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines ref_to_write for copying a ValueRef into a ValueWrite."""

from __future__ import annotations

__all__ = [
    'ref_to_write',
]

import typing

from google.protobuf import any_pb2
from google.protobuf import descriptor
from google.protobuf import descriptor_pool
from google.protobuf import json_format
from google.protobuf import message
from google.protobuf import message_factory

from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2
from turboci.utils import value
from turboci.utils.value import data_source


def ref_to_write(
    ds: data_source.DataSource,
    ref: value_ref_pb2.ValueRef,
    *,
    pool: None | descriptor_pool.DescriptorPool = None,
) -> value_write_pb2.ValueWrite:
  """Copies a ValueRef into a new ValueWrite.

  This does NOT recompute Tags. If ValueRef has binary data, this mints a new
  ValueWrite directly. If the ValueRef has a JSON representation, this needs
  to re-encode the JSON to binary, and may raise ValueError.

  This is useful to copy a ValueRef discovered via a query or read of some
  node into a new node.

  Args:
    ds: A DataSource used to pull ValueData by digest.
    ref: The ValueRef to copy into a ValueWrite.
    pool: Optional DescriptorPool for resolving `ref.type_url` when re-encoding
      JSON data. Defaults to `descriptor_pool.Default()`.

  Returns:
    A new ValueWrite containing binary data, realm, and tags from `ref`.

  Raises:
    OmittedDataError: If `ref` has `omit_reason` set.
    ValueError: If `ref`'s descriptor cannot be found, its data is missing, or
      its JSON representation cannot be re-encoded to binary.
  """
  try:
    data = value.get_data(ds, ref)
  except value.OmittedDataError as ex:
    raise value.OmittedDataError(
        ex.omit_reason, prefix='ref cannot be copied'
    ) from ex
  if data is not None and data.HasField('binary'):
    return value_write_pb2.ValueWrite(
        data=data.binary,
        realm=ref.realm,
        tags=ref.tags,
    )

  dpool: descriptor_pool.DescriptorPool = (
      pool
      if pool is not None
      else typing.cast(
          descriptor_pool.DescriptorPool, descriptor_pool.Default()
      )
  )
  if not ref.type_url.startswith(value.TYPE_URL_PREFIX):
    raise ValueError(
        'ref cannot be copied: error getting descriptor for'
        f' {ref.type_url!r}: missing {value.TYPE_URL_PREFIX!r} prefix'
    )
  msg_name = ref.type_url.removeprefix(value.TYPE_URL_PREFIX)
  try:
    desc = typing.cast(
        descriptor.Descriptor, dpool.FindMessageTypeByName(msg_name)
    )
  except KeyError as ex:
    raise ValueError(
        f'ref cannot be copied: error getting descriptor for {ref.type_url!r}:'
        f' {ex}'
    ) from ex

  if data is None or not data.HasField('json'):
    raise ValueError(f'ref cannot be copied: missing data for {ref.type_url!r}')

  dec = message_factory.GetMessageClass(desc)()
  try:
    json_format.Parse(data.json.value, dec, descriptor_pool=dpool)
  except json_format.ParseError as ex:
    raise ValueError(
        f'ref cannot be copied: error unmarshaling JSON representation: {ex}'
    ) from ex

  enc_any = any_pb2.Any()
  try:
    enc_any.Pack(dec, deterministic=True)
  except message.EncodeError as ex:
    raise ValueError(
        'ref cannot be copied: error marshaling decoded JSON representation:'
        f' {ex}'
    ) from ex

  return value_write_pb2.ValueWrite(
      data=enc_any,
      realm=ref.realm,
      tags=ref.tags,
  )
