from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor
TAG_FIELD_NUMBER: _ClassVar[int]
tag: _descriptor.FieldDescriptor

class Tag(_message.Message):
    __slots__ = ("indexed", "index_key_only", "alt_key", "capture_unset")
    INDEXED_FIELD_NUMBER: _ClassVar[int]
    INDEX_KEY_ONLY_FIELD_NUMBER: _ClassVar[int]
    ALT_KEY_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_UNSET_FIELD_NUMBER: _ClassVar[int]
    indexed: bool
    index_key_only: bool
    alt_key: _containers.RepeatedScalarFieldContainer[str]
    capture_unset: bool
    def __init__(self, indexed: _Optional[bool] = ..., index_key_only: _Optional[bool] = ..., alt_key: _Optional[_Iterable[str]] = ..., capture_unset: _Optional[bool] = ...) -> None: ...
