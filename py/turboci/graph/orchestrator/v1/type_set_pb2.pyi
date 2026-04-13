from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TypeSet(_message.Message):
    __slots__ = ("type_urls",)
    TYPE_URLS_FIELD_NUMBER: _ClassVar[int]
    type_urls: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type_urls: _Optional[_Iterable[str]] = ...) -> None: ...
