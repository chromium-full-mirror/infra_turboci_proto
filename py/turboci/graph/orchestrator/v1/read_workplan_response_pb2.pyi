from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2 as _value_data_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2 as _workplan_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadWorkPlanResponse(_message.Message):
    __slots__ = ("workplan", "value_data", "current_attempt_state", "version", "pagination_token", "next_page_token")
    class ValueDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _value_data_pb2.ValueData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_value_data_pb2.ValueData, _Mapping]] = ...) -> None: ...
    WORKPLAN_FIELD_NUMBER: _ClassVar[int]
    VALUE_DATA_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    workplan: _workplan_pb2.WorkPlan
    value_data: _containers.MessageMap[str, _value_data_pb2.ValueData]
    current_attempt_state: _stage_pb2.StageAttemptCurrentState
    version: _revision_pb2.Revision
    pagination_token: str
    next_page_token: str
    def __init__(self, workplan: _Optional[_Union[_workplan_pb2.WorkPlan, _Mapping]] = ..., value_data: _Optional[_Mapping[str, _value_data_pb2.ValueData]] = ..., current_attempt_state: _Optional[_Union[_stage_pb2.StageAttemptCurrentState, _Mapping]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., pagination_token: _Optional[str] = ..., next_page_token: _Optional[str] = ...) -> None: ...
