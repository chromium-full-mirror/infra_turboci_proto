# Copyright 2026 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Tests for TurboCI client transports."""

from __future__ import annotations

import dataclasses
import datetime
import typing
import unittest
from unittest import mock

from google.protobuf import empty_pb2
from google.rpc import code_pb2
import grpc
from turboci.utils import client


class _Metadatum(typing.Protocol):
  key: str
  value: str


_Metadata: typing.TypeAlias = tuple[tuple[str, str | bytes], ...]


@typing.final
@dataclasses.dataclass
class MockRpcError(grpc.RpcError, grpc.Call):
  """A real exception class that implements grpc.RpcError and grpc.Call."""

  def __init__(
      self,
      code: grpc.StatusCode,
      details: str,
      metadata: tuple[_Metadatum, ...] = (),
  ):
    super().__init__()
    self._code = code
    self._details = details
    self._metadata = metadata

  def code(self) -> grpc.StatusCode:
    return self._code

  def details(self) -> str:
    return self._details

  def trailing_metadata(  # pyright: ignore [reportIncompatibleMethodOverride]
      self,
  ) -> tuple[_Metadatum, ...]:
    return self._metadata

  def add_callback(self, callback: typing.Callable[[], None]) -> bool:
    raise NotImplementedError()

  def cancel(self) -> bool:
    raise NotImplementedError()

  def is_active(self) -> bool:
    raise NotImplementedError()

  def time_remaining(self) -> float:
    raise NotImplementedError()

  def initial_metadata(self) -> _Metadata:
    raise NotImplementedError()


class TestTransports(unittest.TestCase):

  def test_grpc_transport_success(self):
    mock_channel = mock.Mock()
    mock_method = mock.Mock()
    mock_channel.unary_unary.return_value = mock_method

    mock_response = empty_pb2.Empty()
    mock_method.return_value = mock_response

    transport = client.GrpcTransport(mock_channel)
    request = empty_pb2.Empty()
    options = client.CallOptions(
        deadline=datetime.timedelta(seconds=5), metadata={'key': 'value'}
    )

    res = transport.call_unary('CreateWorkPlan', request, options)

    self.assertEqual(res, mock_response)
    mock_method.assert_called_once_with(
        request, timeout=5.0, metadata=[('key', 'value')]
    )

  def test_grpc_transport_error(self):
    mock_channel = mock.Mock()
    mock_method = mock.Mock()
    mock_channel.unary_unary.return_value = mock_method

    # Use the real MockRpcError exception
    mock_err = MockRpcError(grpc.StatusCode.NOT_FOUND, 'not found')
    mock_method.side_effect = mock_err

    transport = client.GrpcTransport(mock_channel)
    request = empty_pb2.Empty()

    with self.assertRaises(client.RPCError) as ctx:
      transport.call_unary('CreateWorkPlan', request)

    self.assertEqual(ctx.exception.status.code, code_pb2.NOT_FOUND)
    self.assertEqual(str(ctx.exception), 'NOT_FOUND: not found')


class TestTransportsAsync(unittest.IsolatedAsyncioTestCase):

  async def test_grpc_async_transport_success(self):
    mock_channel = mock.Mock()
    mock_method = mock.AsyncMock()
    mock_channel.unary_unary.return_value = mock_method

    mock_response = empty_pb2.Empty()
    mock_method.return_value = mock_response

    transport = client.GrpcAsyncTransport(mock_channel)
    request = empty_pb2.Empty()
    options = client.CallOptions(
        deadline=datetime.timedelta(seconds=5), metadata={'key': 'value'}
    )

    res = await transport.call_unary('CreateWorkPlan', request, options)

    self.assertEqual(res, mock_response)
    mock_method.assert_called_once_with(
        request, timeout=5.0, metadata=[('key', 'value')]
    )

  async def test_grpc_async_transport_error(self):
    mock_channel = mock.Mock()
    mock_method = mock.AsyncMock()
    mock_channel.unary_unary.return_value = mock_method

    # Use the real MockRpcError exception
    mock_err = MockRpcError(grpc.StatusCode.NOT_FOUND, 'not found')
    mock_method.side_effect = mock_err

    transport = client.GrpcAsyncTransport(mock_channel)
    request = empty_pb2.Empty()

    with self.assertRaises(client.RPCError) as ctx:
      await transport.call_unary('CreateWorkPlan', request)

    self.assertEqual(ctx.exception.status.code, code_pb2.NOT_FOUND)
    self.assertEqual(str(ctx.exception), 'NOT_FOUND: not found')


if __name__ == '__main__':
  unittest.main()
