from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import evaluation_error_pb2 as _evaluation_error_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AttributeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ATTRIBUTE_TYPE_UNKNOWN: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_BOOL: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_BOOL_LIST: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_INT64: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_INT64_LIST: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_STRING: _ClassVar[AttributeType]
    ATTRIBUTE_TYPE_STRING_LIST: _ClassVar[AttributeType]
ATTRIBUTE_TYPE_UNKNOWN: AttributeType
ATTRIBUTE_TYPE_BOOL: AttributeType
ATTRIBUTE_TYPE_BOOL_LIST: AttributeType
ATTRIBUTE_TYPE_INT64: AttributeType
ATTRIBUTE_TYPE_INT64_LIST: AttributeType
ATTRIBUTE_TYPE_STRING: AttributeType
ATTRIBUTE_TYPE_STRING_LIST: AttributeType

class Attribute(_message.Message):
    __slots__ = ("name", "expression", "on_stage_state", "on_check_state", "attribute_type", "resolved_at", "error_result", "int_results", "str_results", "bool_results")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    ON_STAGE_STATE_FIELD_NUMBER: _ClassVar[int]
    ON_CHECK_STATE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_RESULT_FIELD_NUMBER: _ClassVar[int]
    INT_RESULTS_FIELD_NUMBER: _ClassVar[int]
    STR_RESULTS_FIELD_NUMBER: _ClassVar[int]
    BOOL_RESULTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    expression: str
    on_stage_state: _stage_state_pb2.StageState
    on_check_state: _check_state_pb2.CheckState
    attribute_type: AttributeType
    resolved_at: _revision_pb2.Revision
    error_result: _evaluation_error_pb2.EvaluationError
    int_results: _containers.RepeatedScalarFieldContainer[int]
    str_results: _containers.RepeatedScalarFieldContainer[str]
    bool_results: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, name: _Optional[str] = ..., expression: _Optional[str] = ..., on_stage_state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., on_check_state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., attribute_type: _Optional[_Union[AttributeType, str]] = ..., resolved_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., error_result: _Optional[_Union[_evaluation_error_pb2.EvaluationError, _Mapping]] = ..., int_results: _Optional[_Iterable[int]] = ..., str_results: _Optional[_Iterable[str]] = ..., bool_results: _Optional[_Iterable[bool]] = ...) -> None: ...
