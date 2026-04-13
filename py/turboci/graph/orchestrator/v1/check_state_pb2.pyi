from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CheckState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHECK_STATE_UNKNOWN: _ClassVar[CheckState]
    CHECK_STATE_PLANNING: _ClassVar[CheckState]
    CHECK_STATE_PLANNED: _ClassVar[CheckState]
    CHECK_STATE_WAITING: _ClassVar[CheckState]
    CHECK_STATE_FINAL: _ClassVar[CheckState]
CHECK_STATE_UNKNOWN: CheckState
CHECK_STATE_PLANNING: CheckState
CHECK_STATE_PLANNED: CheckState
CHECK_STATE_WAITING: CheckState
CHECK_STATE_FINAL: CheckState
