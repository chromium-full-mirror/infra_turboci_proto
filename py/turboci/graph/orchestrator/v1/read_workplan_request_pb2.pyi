from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.ids.v1 import identifier_kind_pb2 as _identifier_kind_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import value_filter_pb2 as _value_filter_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadWorkPlanRequest(_message.Message):
    __slots__ = ("token", "workplan_id", "included_node_types", "since_version", "value_filter", "pagination_token", "page_size", "page_token")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDED_NODE_TYPES_FIELD_NUMBER: _ClassVar[int]
    SINCE_VERSION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    workplan_id: _identifier_pb2.WorkPlan
    included_node_types: _containers.RepeatedScalarFieldContainer[_identifier_kind_pb2.IdentifierKind]
    since_version: _revision_pb2.Revision
    value_filter: _value_filter_pb2.ValueFilter
    pagination_token: str
    page_size: int
    page_token: str
    def __init__(self, token: _Optional[str] = ..., workplan_id: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., included_node_types: _Optional[_Iterable[_Union[_identifier_kind_pb2.IdentifierKind, str]]] = ..., since_version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., value_filter: _Optional[_Union[_value_filter_pb2.ValueFilter, _Mapping]] = ..., pagination_token: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...
