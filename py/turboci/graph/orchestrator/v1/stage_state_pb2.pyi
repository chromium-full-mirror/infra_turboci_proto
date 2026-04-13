from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class StageState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_STATE_UNKNOWN: _ClassVar[StageState]
    STAGE_STATE_PLANNED: _ClassVar[StageState]
    STAGE_STATE_ATTEMPTING: _ClassVar[StageState]
    STAGE_STATE_AWAITING_GROUP: _ClassVar[StageState]
    STAGE_STATE_FINAL: _ClassVar[StageState]
STAGE_STATE_UNKNOWN: StageState
STAGE_STATE_PLANNED: StageState
STAGE_STATE_ATTEMPTING: StageState
STAGE_STATE_AWAITING_GROUP: StageState
STAGE_STATE_FINAL: StageState
