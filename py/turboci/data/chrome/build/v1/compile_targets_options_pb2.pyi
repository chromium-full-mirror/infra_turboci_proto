from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CompileTargetsOptions(_message.Message):
    __slots__ = ("compile_targets",)
    COMPILE_TARGETS_FIELD_NUMBER: _ClassVar[int]
    compile_targets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, compile_targets: _Optional[_Iterable[str]] = ...) -> None: ...
