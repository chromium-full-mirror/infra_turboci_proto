from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2 as _value_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CancelStageRequest(_message.Message):
    __slots__ = ("stage", "value_data", "attempt", "stage_attempt_token")
    class ValueDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _value_data_pb2.ValueData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_value_data_pb2.ValueData, _Mapping]] = ...) -> None: ...
    STAGE_FIELD_NUMBER: _ClassVar[int]
    VALUE_DATA_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    STAGE_ATTEMPT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    stage: _stage_pb2.Stage
    value_data: _containers.MessageMap[str, _value_data_pb2.ValueData]
    attempt: _identifier_pb2.StageAttempt
    stage_attempt_token: str
    def __init__(self, stage: _Optional[_Union[_stage_pb2.Stage, _Mapping]] = ..., value_data: _Optional[_Mapping[str, _value_data_pb2.ValueData]] = ..., attempt: _Optional[_Union[_identifier_pb2.StageAttempt, _Mapping]] = ..., stage_attempt_token: _Optional[str] = ...) -> None: ...

class CancelStageResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
