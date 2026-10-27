from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import value_data_pb2 as _value_data_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2 as _workplan_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryNodesResponse(_message.Message):
    __slots__ = ("workplans", "workplan", "value_data", "selected", "current_attempt_state", "version", "next_page_token")
    class ValueDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _value_data_pb2.ValueData
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_value_data_pb2.ValueData, _Mapping]] = ...) -> None: ...
    class SelectedNode(_message.Message):
        __slots__ = ("node", "disposition", "matched_filter")
        class Disposition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DISPOSITION_UNKNOWN: _ClassVar[QueryNodesResponse.SelectedNode.Disposition]
            DISPOSITION_FOUND: _ClassVar[QueryNodesResponse.SelectedNode.Disposition]
            DISPOSITION_NOT_FOUND: _ClassVar[QueryNodesResponse.SelectedNode.Disposition]
            DISPOSITION_PERMISSION_DENIED: _ClassVar[QueryNodesResponse.SelectedNode.Disposition]
        DISPOSITION_UNKNOWN: QueryNodesResponse.SelectedNode.Disposition
        DISPOSITION_FOUND: QueryNodesResponse.SelectedNode.Disposition
        DISPOSITION_NOT_FOUND: QueryNodesResponse.SelectedNode.Disposition
        DISPOSITION_PERMISSION_DENIED: QueryNodesResponse.SelectedNode.Disposition
        NODE_FIELD_NUMBER: _ClassVar[int]
        DISPOSITION_FIELD_NUMBER: _ClassVar[int]
        MATCHED_FILTER_FIELD_NUMBER: _ClassVar[int]
        node: _identifier_pb2.Identifier
        disposition: QueryNodesResponse.SelectedNode.Disposition
        matched_filter: bool
        def __init__(self, node: _Optional[_Union[_identifier_pb2.Identifier, _Mapping]] = ..., disposition: _Optional[_Union[QueryNodesResponse.SelectedNode.Disposition, str]] = ..., matched_filter: _Optional[bool] = ...) -> None: ...
    WORKPLANS_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_FIELD_NUMBER: _ClassVar[int]
    VALUE_DATA_FIELD_NUMBER: _ClassVar[int]
    SELECTED_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    workplans: _containers.RepeatedCompositeFieldContainer[_workplan_pb2.WorkPlan]
    workplan: _workplan_pb2.WorkPlan
    value_data: _containers.MessageMap[str, _value_data_pb2.ValueData]
    selected: _containers.RepeatedCompositeFieldContainer[QueryNodesResponse.SelectedNode]
    current_attempt_state: _stage_pb2.StageAttemptCurrentState
    version: _revision_pb2.Revision
    next_page_token: str
    def __init__(self, workplans: _Optional[_Iterable[_Union[_workplan_pb2.WorkPlan, _Mapping]]] = ..., workplan: _Optional[_Union[_workplan_pb2.WorkPlan, _Mapping]] = ..., value_data: _Optional[_Mapping[str, _value_data_pb2.ValueData]] = ..., selected: _Optional[_Iterable[_Union[QueryNodesResponse.SelectedNode, _Mapping]]] = ..., current_attempt_state: _Optional[_Union[_stage_pb2.StageAttemptCurrentState, _Mapping]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
