import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_execution_policy_pb2 as _stage_attempt_execution_policy_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StageExecutionPolicy(_message.Message):
    __slots__ = ("retry", "stage_timeout", "execute_at_least_one_attempt", "attempt_execution_policy_template", "throttle_first_attempt_until")
    class Retry(_message.Message):
        __slots__ = ("max_retries",)
        MAX_RETRIES_FIELD_NUMBER: _ClassVar[int]
        max_retries: int
        def __init__(self, max_retries: _Optional[int] = ...) -> None: ...
    RETRY_FIELD_NUMBER: _ClassVar[int]
    STAGE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_AT_LEAST_ONE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_EXECUTION_POLICY_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    THROTTLE_FIRST_ATTEMPT_UNTIL_FIELD_NUMBER: _ClassVar[int]
    retry: StageExecutionPolicy.Retry
    stage_timeout: _duration_pb2.Duration
    execute_at_least_one_attempt: bool
    attempt_execution_policy_template: _stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy
    throttle_first_attempt_until: _timestamp_pb2.Timestamp
    def __init__(self, retry: _Optional[_Union[StageExecutionPolicy.Retry, _Mapping]] = ..., stage_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., execute_at_least_one_attempt: _Optional[bool] = ..., attempt_execution_policy_template: _Optional[_Union[_stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy, _Mapping]] = ..., throttle_first_attempt_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
