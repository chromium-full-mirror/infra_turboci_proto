from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class StageAttemptState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_ATTEMPT_STATE_UNKNOWN: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_PENDING: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_THROTTLED: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_SCHEDULED: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_RUNNING: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_CANCELLING: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_TEARING_DOWN: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_COMPLETE: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_INCOMPLETE: _ClassVar[StageAttemptState]
    STAGE_ATTEMPT_STATE_AWAITING_RETRY: _ClassVar[StageAttemptState]
STAGE_ATTEMPT_STATE_UNKNOWN: StageAttemptState
STAGE_ATTEMPT_STATE_PENDING: StageAttemptState
STAGE_ATTEMPT_STATE_THROTTLED: StageAttemptState
STAGE_ATTEMPT_STATE_SCHEDULED: StageAttemptState
STAGE_ATTEMPT_STATE_RUNNING: StageAttemptState
STAGE_ATTEMPT_STATE_CANCELLING: StageAttemptState
STAGE_ATTEMPT_STATE_TEARING_DOWN: StageAttemptState
STAGE_ATTEMPT_STATE_COMPLETE: StageAttemptState
STAGE_ATTEMPT_STATE_INCOMPLETE: StageAttemptState
STAGE_ATTEMPT_STATE_AWAITING_RETRY: StageAttemptState
