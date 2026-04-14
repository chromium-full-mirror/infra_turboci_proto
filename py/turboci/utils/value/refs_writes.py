# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Defines helpers for creating ValueRef and ValueWrite messages."""

from __future__ import annotations

__all__ = [
    'SpecialRealm',
    'TYPE_URL_PREFIX',
    'ref',
    'ref_from_write',
    'url',
    'write',
]

import typing

from google.protobuf import message
from google.protobuf import any_pb2

from turboci.graph.orchestrator.v1 import value_ref_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2

# The standard type url prefix used by any_pb2.Any.
TYPE_URL_PREFIX = 'type.googleapis.com/'


def url(msg: message.Message | type[message.Message]) -> str:
  """Helper to get the type_url from a proto message.

  Useful for tests.

  Args:
    msg: The proto message type or instance.

  Returns:
    The type_url used by any_pb2.Any (e.g. type.googleapis.com/...)
  """
  return f'{TYPE_URL_PREFIX}{msg.DESCRIPTOR.full_name}'


def write(
    data: message.Message,
    realm: str | SpecialRealm = '$from_container',
) -> value_write_pb2.ValueWrite:
  """Makes a ValueWrite.

  The SpecialRealm forms have the following meanings:
    * '' - This value must already exist in the DB. For example, if you are
      updating an existing Check Option, you can use this to indicate that
      the value must already exist, and write permission in this existing
      realm will be used.
    * '$from_token' - This will use the realm encoded in the token you provide
      with the WriteNodes RPC call. If the token is from WorkPlan creation,
      the realm is the realm of the WorkPlan. If the token is from Stage
      execution (that is; you are calling as part of a Stage Attempt), then the
      realm is that of the Stage you are running as.
    * '$from_container' - This will use the realm of the containing object.
      Stages and Checks are contained in their WorkPlan. Values (options,
      results, attempt details, etc.) are contained in their respective Stage
      or Check.

  Args:
    data: Proto message to store. As a convenience, if this is literally
      any_pb2.Any, it's used verbatim.
    realm: The security realm for this ref. `SpecialRealm` forms are permitted.
      Defaults to '$from_container'.

  Returns:
    A ValueWrite with data set to the Any-packed version of `data`.
  """
  apb: any_pb2.Any
  if isinstance(data, any_pb2.Any):
    apb = data
  else:
    apb = any_pb2.Any()
    apb.Pack(data, deterministic=True)
  return value_write_pb2.ValueWrite(data=apb, realm=realm)


def ref(data: message.Message, realm: str) -> value_ref_pb2.ValueRef:
  """Makes an inline ValueRef.

  Useful for testing.

  Args:
    data: Proto message to store `inline`.
    realm: The security realm for this ref.

  Returns:
    A ValueRef with inline set to the Any-packed version of `data`.

  Raises:
    ValueError if realm is a `SpecialRealm` form.
  """
  return ref_from_write(write(data, realm))


# Special forms for `realm` usable as ValueWrite.realm.
#
# Helper type to let the IDE autocomplete these special forms via the LSP when
# invoking `write`.
#
# It would be nicer if the LSP could autocomplete symbols of some kind rather
# than just raw strings, but I think this is a decently nice experience.
SpecialRealm = typing.Literal[
    '',  # Value must already exist in DB.
    '$from_container',  # Inherit container (workplan, stage or check) realm.
    '$from_token',  # Inherit realm from RPC token.
]


def ref_from_write(
    val_write: value_write_pb2.ValueWrite,
) -> value_ref_pb2.ValueRef:
  """Returns a ValueRef (with inline data) for a ValueWrite.

  Useful for testing.

  Args:
    val_write: The ValueWrite to convert.

  Returns:
    A ValueRef populated from `val_write`

  Raises:
    ValueError if val_write.realm is a `SpecialRealm` form.
  """
  if val_write.realm in ('', '$from_container', '$from_token'):
    raise ValueError(f'invalid realm for ValueRef: {val_write.realm!r}')

  return value_ref_pb2.ValueRef(
      type_url=val_write.data.type_url,
      inline=val_write.data,
      realm=val_write.realm,
  )
