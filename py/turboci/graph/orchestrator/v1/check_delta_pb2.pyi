from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import dependencies_pb2 as _dependencies_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckDelta(_message.Message):
    __slots__ = ("state", "dependencies", "options", "results")
    class Result(_message.Message):
        __slots__ = ("identifier", "created", "data", "finalized")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        CREATED_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        FINALIZED_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.CheckResult
        created: bool
        data: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
        finalized: bool
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.CheckResult, _Mapping]] = ..., created: _Optional[bool] = ..., data: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., finalized: _Optional[bool] = ...) -> None: ...
    STATE_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    state: _check_state_pb2.CheckState
    dependencies: _dependencies_pb2.Dependencies
    options: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
    results: _containers.RepeatedCompositeFieldContainer[CheckDelta.Result]
    def __init__(self, state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., dependencies: _Optional[_Union[_dependencies_pb2.Dependencies, _Mapping]] = ..., options: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[CheckDelta.Result, _Mapping]]] = ...) -> None: ...
