import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.rpc import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProgressEvolvePending(_message.Message):
    __slots__ = ("next_try", "pre_rpc", "rpc")
    NEXT_TRY_FIELD_NUMBER: _ClassVar[int]
    PRE_RPC_FIELD_NUMBER: _ClassVar[int]
    RPC_FIELD_NUMBER: _ClassVar[int]
    next_try: _timestamp_pb2.Timestamp
    pre_rpc: _status_pb2.Status
    rpc: _status_pb2.Status
    def __init__(self, next_try: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., pre_rpc: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., rpc: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class ProgressIgnoredDetail(_message.Message):
    __slots__ = ("type_url",)
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    type_url: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type_url: _Optional[_Iterable[str]] = ...) -> None: ...
