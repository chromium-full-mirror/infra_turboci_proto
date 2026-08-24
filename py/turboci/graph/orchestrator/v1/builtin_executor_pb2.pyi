from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class BuiltinExecutor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUILTIN_EXECUTOR_UNKNOWN: _ClassVar[BuiltinExecutor]
    BUILTIN_EXECUTOR_NOOP: _ClassVar[BuiltinExecutor]
BUILTIN_EXECUTOR_UNKNOWN: BuiltinExecutor
BUILTIN_EXECUTOR_NOOP: BuiltinExecutor
