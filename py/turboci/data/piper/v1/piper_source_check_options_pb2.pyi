from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PiperSourceCheckOptions(_message.Message):
    __slots__ = ("files", "targets", "cl_number")
    FILES_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    CL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedScalarFieldContainer[str]
    targets: _containers.RepeatedScalarFieldContainer[str]
    cl_number: int
    def __init__(self, files: _Optional[_Iterable[str]] = ..., targets: _Optional[_Iterable[str]] = ..., cl_number: _Optional[int] = ...) -> None: ...
