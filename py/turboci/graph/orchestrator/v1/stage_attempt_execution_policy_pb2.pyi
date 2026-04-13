import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StageAttemptExecutionPolicy(_message.Message):
    __slots__ = ("heartbeat", "timeout")
    class Heartbeat(_message.Message):
        __slots__ = ("scheduled", "running", "tearing_down")
        SCHEDULED_FIELD_NUMBER: _ClassVar[int]
        RUNNING_FIELD_NUMBER: _ClassVar[int]
        TEARING_DOWN_FIELD_NUMBER: _ClassVar[int]
        scheduled: _duration_pb2.Duration
        running: _duration_pb2.Duration
        tearing_down: _duration_pb2.Duration
        def __init__(self, scheduled: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., running: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., tearing_down: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class Timeout(_message.Message):
        __slots__ = ("pending_throttled", "scheduled", "running", "tearing_down")
        PENDING_THROTTLED_FIELD_NUMBER: _ClassVar[int]
        SCHEDULED_FIELD_NUMBER: _ClassVar[int]
        RUNNING_FIELD_NUMBER: _ClassVar[int]
        TEARING_DOWN_FIELD_NUMBER: _ClassVar[int]
        pending_throttled: _duration_pb2.Duration
        scheduled: _duration_pb2.Duration
        running: _duration_pb2.Duration
        tearing_down: _duration_pb2.Duration
        def __init__(self, pending_throttled: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., scheduled: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., running: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., tearing_down: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    heartbeat: StageAttemptExecutionPolicy.Heartbeat
    timeout: StageAttemptExecutionPolicy.Timeout
    def __init__(self, heartbeat: _Optional[_Union[StageAttemptExecutionPolicy.Heartbeat, _Mapping]] = ..., timeout: _Optional[_Union[StageAttemptExecutionPolicy.Timeout, _Mapping]] = ...) -> None: ...
