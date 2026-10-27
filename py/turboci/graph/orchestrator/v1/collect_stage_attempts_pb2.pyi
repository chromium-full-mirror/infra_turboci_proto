from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CollectStageAttempts(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLLECT_STAGE_ATTEMPTS_UNKNOWN: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_NONE: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_ALL: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_LATEST: _ClassVar[CollectStageAttempts]
COLLECT_STAGE_ATTEMPTS_UNKNOWN: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_NONE: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_ALL: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_LATEST: CollectStageAttempts
