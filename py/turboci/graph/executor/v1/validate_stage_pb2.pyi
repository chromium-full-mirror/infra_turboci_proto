from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import stage_execution_policy_pb2 as _stage_execution_policy_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2 as _value_data_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2 as _workplan_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidateStageRequest(_message.Message):
    __slots__ = ("stage", "workplan", "value_data")
    class ValueDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _value_data_pb2.ValueData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_value_data_pb2.ValueData, _Mapping]] = ...) -> None: ...
    STAGE_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_FIELD_NUMBER: _ClassVar[int]
    VALUE_DATA_FIELD_NUMBER: _ClassVar[int]
    stage: _stage_pb2.Stage
    workplan: _workplan_pb2.WorkPlan
    value_data: _containers.MessageMap[str, _value_data_pb2.ValueData]
    def __init__(self, stage: _Optional[_Union[_stage_pb2.Stage, _Mapping]] = ..., workplan: _Optional[_Union[_workplan_pb2.WorkPlan, _Mapping]] = ..., value_data: _Optional[_Mapping[str, _value_data_pb2.ValueData]] = ...) -> None: ...

class ValidateStageResponse(_message.Message):
    __slots__ = ("stage_execution_policy", "stage_service_accounts", "stage_sub_type")
    STAGE_EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    STAGE_SERVICE_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    STAGE_SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
    stage_execution_policy: _stage_execution_policy_pb2.StageExecutionPolicy
    stage_service_accounts: _containers.RepeatedScalarFieldContainer[str]
    stage_sub_type: str
    def __init__(self, stage_execution_policy: _Optional[_Union[_stage_execution_policy_pb2.StageExecutionPolicy, _Mapping]] = ..., stage_service_accounts: _Optional[_Iterable[str]] = ..., stage_sub_type: _Optional[str] = ...) -> None: ...
