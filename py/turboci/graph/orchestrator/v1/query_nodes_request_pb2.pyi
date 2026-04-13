from turboci.graph.orchestrator.v1 import query_pb2 as _query_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import type_info_pb2 as _type_info_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryNodesRequest(_message.Message):
    __slots__ = ("token", "type_info", "version", "query")
    class VersionRestriction(_message.Message):
        __slots__ = ("require", "snapshot")
        REQUIRE_FIELD_NUMBER: _ClassVar[int]
        SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
        require: _revision_pb2.Revision
        snapshot: _revision_pb2.Revision
        def __init__(self, require: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., snapshot: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    TYPE_INFO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    token: str
    type_info: _type_info_pb2.TypeInfo
    version: QueryNodesRequest.VersionRestriction
    query: _containers.RepeatedCompositeFieldContainer[_query_pb2.Query]
    def __init__(self, token: _Optional[str] = ..., type_info: _Optional[_Union[_type_info_pb2.TypeInfo, _Mapping]] = ..., version: _Optional[_Union[QueryNodesRequest.VersionRestriction, _Mapping]] = ..., query: _Optional[_Iterable[_Union[_query_pb2.Query, _Mapping]]] = ...) -> None: ...
