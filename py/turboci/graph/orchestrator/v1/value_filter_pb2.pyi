from turboci.graph.orchestrator.v1 import type_info_pb2 as _type_info_pb2
from turboci.graph.orchestrator.v1 import value_mask_pb2 as _value_mask_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2 as _value_slot_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValueFilter(_message.Message):
    __slots__ = ("type_info", "include_data", "check_options", "check_result_data", "check_edit_options", "check_edit_result_data", "stage_args", "stage_attempt_details", "stage_attempt_progress_details", "stage_edit_attempt_details", "stage_edit_attempt_progress_details", "stage_legacy_worknode")
    TYPE_INFO_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_DATA_FIELD_NUMBER: _ClassVar[int]
    CHECK_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CHECK_RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    CHECK_EDIT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CHECK_EDIT_RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    STAGE_ARGS_FIELD_NUMBER: _ClassVar[int]
    STAGE_ATTEMPT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STAGE_ATTEMPT_PROGRESS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STAGE_EDIT_ATTEMPT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STAGE_EDIT_ATTEMPT_PROGRESS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STAGE_LEGACY_WORKNODE_FIELD_NUMBER: _ClassVar[int]
    type_info: _type_info_pb2.TypeInfo
    include_data: _containers.RepeatedScalarFieldContainer[_value_slot_pb2.ValueSlot]
    check_options: _value_mask_pb2.ValueMask
    check_result_data: _value_mask_pb2.ValueMask
    check_edit_options: _value_mask_pb2.ValueMask
    check_edit_result_data: _value_mask_pb2.ValueMask
    stage_args: _value_mask_pb2.ValueMask
    stage_attempt_details: _value_mask_pb2.ValueMask
    stage_attempt_progress_details: _value_mask_pb2.ValueMask
    stage_edit_attempt_details: _value_mask_pb2.ValueMask
    stage_edit_attempt_progress_details: _value_mask_pb2.ValueMask
    stage_legacy_worknode: _value_mask_pb2.ValueMask
    def __init__(self, type_info: _Optional[_Union[_type_info_pb2.TypeInfo, _Mapping]] = ..., include_data: _Optional[_Iterable[_Union[_value_slot_pb2.ValueSlot, str]]] = ..., check_options: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., check_result_data: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., check_edit_options: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., check_edit_result_data: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_args: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_attempt_details: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_attempt_progress_details: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_edit_attempt_details: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_edit_attempt_progress_details: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ..., stage_legacy_worknode: _Optional[_Union[_value_mask_pb2.ValueMask, str]] = ...) -> None: ...
