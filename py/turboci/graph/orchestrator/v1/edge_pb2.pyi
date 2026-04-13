from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Resolution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESOLUTION_UNKNOWN: _ClassVar[Resolution]
    RESOLUTION_SATISFIED: _ClassVar[Resolution]
    RESOLUTION_UNSATISFIED: _ClassVar[Resolution]
RESOLUTION_UNKNOWN: Resolution
RESOLUTION_SATISFIED: Resolution
RESOLUTION_UNSATISFIED: Resolution

class Edge(_message.Message):
    __slots__ = ("check", "stage")
    class Check(_message.Message):
        __slots__ = ("identifier", "condition")
        class Condition(_message.Message):
            __slots__ = ("on_state", "expression")
            ON_STATE_FIELD_NUMBER: _ClassVar[int]
            EXPRESSION_FIELD_NUMBER: _ClassVar[int]
            on_state: _check_state_pb2.CheckState
            expression: str
            def __init__(self, on_state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., expression: _Optional[str] = ...) -> None: ...
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        CONDITION_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.Check
        condition: Edge.Check.Condition
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Check, _Mapping]] = ..., condition: _Optional[_Union[Edge.Check.Condition, _Mapping]] = ...) -> None: ...
    class Stage(_message.Message):
        __slots__ = ("identifier", "condition")
        class Condition(_message.Message):
            __slots__ = ("on_state", "expression")
            ON_STATE_FIELD_NUMBER: _ClassVar[int]
            EXPRESSION_FIELD_NUMBER: _ClassVar[int]
            on_state: _stage_state_pb2.StageState
            expression: str
            def __init__(self, on_state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., expression: _Optional[str] = ...) -> None: ...
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        CONDITION_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.Stage
        condition: Edge.Stage.Condition
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Stage, _Mapping]] = ..., condition: _Optional[_Union[Edge.Stage.Condition, _Mapping]] = ...) -> None: ...
    CHECK_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    check: Edge.Check
    stage: Edge.Stage
    def __init__(self, check: _Optional[_Union[Edge.Check, _Mapping]] = ..., stage: _Optional[_Union[Edge.Stage, _Mapping]] = ...) -> None: ...
