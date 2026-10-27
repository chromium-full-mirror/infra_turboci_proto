from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import collect_stage_attempts_pb2 as _collect_stage_attempts_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import node_predicate_pb2 as _node_predicate_pb2
from turboci.graph.orchestrator.v1 import query_pb2 as _query_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import type_info_pb2 as _type_info_pb2
from turboci.graph.orchestrator.v1 import value_filter_pb2 as _value_filter_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryNodesRequest(_message.Message):
    __slots__ = ("token", "workplan", "selected", "filter", "value_filter", "collect_stage_attempts", "type_info", "version", "query", "page_size", "page_token")
    class NodeSetWorkplan(_message.Message):
        __slots__ = ("workplan_id",)
        WORKPLAN_ID_FIELD_NUMBER: _ClassVar[int]
        workplan_id: _identifier_pb2.WorkPlan
        def __init__(self, workplan_id: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ...) -> None: ...
    class NodeSetSelected(_message.Message):
        __slots__ = ("nodes",)
        NODES_FIELD_NUMBER: _ClassVar[int]
        nodes: _containers.RepeatedCompositeFieldContainer[_identifier_pb2.Identifier]
        def __init__(self, nodes: _Optional[_Iterable[_Union[_identifier_pb2.Identifier, _Mapping]]] = ...) -> None: ...
    class VersionRestriction(_message.Message):
        __slots__ = ("require", "snapshot")
        REQUIRE_FIELD_NUMBER: _ClassVar[int]
        SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
        require: _revision_pb2.Revision
        snapshot: _revision_pb2.Revision
        def __init__(self, require: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., snapshot: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_FIELD_NUMBER: _ClassVar[int]
    SELECTED_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FILTER_FIELD_NUMBER: _ClassVar[int]
    COLLECT_STAGE_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    TYPE_INFO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    workplan: QueryNodesRequest.NodeSetWorkplan
    selected: QueryNodesRequest.NodeSetSelected
    filter: _node_predicate_pb2.NodePredicate
    value_filter: _value_filter_pb2.ValueFilter
    collect_stage_attempts: _collect_stage_attempts_pb2.CollectStageAttempts
    type_info: _type_info_pb2.TypeInfo
    version: QueryNodesRequest.VersionRestriction
    query: _containers.RepeatedCompositeFieldContainer[_query_pb2.Query]
    page_size: int
    page_token: str
    def __init__(self, token: _Optional[str] = ..., workplan: _Optional[_Union[QueryNodesRequest.NodeSetWorkplan, _Mapping]] = ..., selected: _Optional[_Union[QueryNodesRequest.NodeSetSelected, _Mapping]] = ..., filter: _Optional[_Union[_node_predicate_pb2.NodePredicate, _Mapping]] = ..., value_filter: _Optional[_Union[_value_filter_pb2.ValueFilter, _Mapping]] = ..., collect_stage_attempts: _Optional[_Union[_collect_stage_attempts_pb2.CollectStageAttempts, str]] = ..., type_info: _Optional[_Union[_type_info_pb2.TypeInfo, _Mapping]] = ..., version: _Optional[_Union[QueryNodesRequest.VersionRestriction, _Mapping]] = ..., query: _Optional[_Iterable[_Union[_query_pb2.Query, _Mapping]]] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...
