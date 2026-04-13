from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import dependencies_pb2 as _dependencies_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2 as _stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StageDelta(_message.Message):
    __slots__ = ("state", "attempts", "cancelled", "continuation_group")
    class Attempt(_message.Message):
        __slots__ = ("identifier", "state", "details", "progress")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        PROGRESS_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.StageAttempt
        state: _stage_attempt_state_pb2.StageAttemptState
        details: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
        progress: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.StageAttempt, _Mapping]] = ..., state: _Optional[_Union[_stage_attempt_state_pb2.StageAttemptState, str]] = ..., details: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., progress: _Optional[_Iterable[int]] = ...) -> None: ...
    STATE_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    CONTINUATION_GROUP_FIELD_NUMBER: _ClassVar[int]
    state: _stage_state_pb2.StageState
    attempts: _containers.RepeatedCompositeFieldContainer[StageDelta.Attempt]
    cancelled: bool
    continuation_group: _dependencies_pb2.Dependencies
    def __init__(self, state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., attempts: _Optional[_Iterable[_Union[StageDelta.Attempt, _Mapping]]] = ..., cancelled: _Optional[bool] = ..., continuation_group: _Optional[_Union[_dependencies_pb2.Dependencies, _Mapping]] = ...) -> None: ...
