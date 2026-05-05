from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class StageConcludedReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_CONCLUDED_REASON_UNKNOWN: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_ATTEMPT_COMPLETE: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_NO_RETRIES_LEFT: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_FINAL_ATTEMPT_BLOCKED_RETRY: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_TIMEOUT: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_CANCELLED: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_NO_EXECUTOR: _ClassVar[StageConcludedReason]
    STAGE_CONCLUDED_REASON_PERMISSION_DENIED: _ClassVar[StageConcludedReason]
STAGE_CONCLUDED_REASON_UNKNOWN: StageConcludedReason
STAGE_CONCLUDED_REASON_ATTEMPT_COMPLETE: StageConcludedReason
STAGE_CONCLUDED_REASON_NO_RETRIES_LEFT: StageConcludedReason
STAGE_CONCLUDED_REASON_FINAL_ATTEMPT_BLOCKED_RETRY: StageConcludedReason
STAGE_CONCLUDED_REASON_TIMEOUT: StageConcludedReason
STAGE_CONCLUDED_REASON_CANCELLED: StageConcludedReason
STAGE_CONCLUDED_REASON_NO_EXECUTOR: StageConcludedReason
STAGE_CONCLUDED_REASON_PERMISSION_DENIED: StageConcludedReason
