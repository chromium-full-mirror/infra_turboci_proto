from turboci.graph.orchestrator.v1 import edge_pb2 as _edge_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dependencies(_message.Message):
    __slots__ = ("edges", "predicate", "resolution_events", "resolution")
    class Group(_message.Message):
        __slots__ = ("edges", "groups", "threshold")
        EDGES_FIELD_NUMBER: _ClassVar[int]
        GROUPS_FIELD_NUMBER: _ClassVar[int]
        THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        edges: _containers.RepeatedScalarFieldContainer[int]
        groups: _containers.RepeatedCompositeFieldContainer[Dependencies.Group]
        threshold: int
        def __init__(self, edges: _Optional[_Iterable[int]] = ..., groups: _Optional[_Iterable[_Union[Dependencies.Group, _Mapping]]] = ..., threshold: _Optional[int] = ...) -> None: ...
    class ResolutionEvent(_message.Message):
        __slots__ = ("version", "resolution", "condition_version")
        VERSION_FIELD_NUMBER: _ClassVar[int]
        RESOLUTION_FIELD_NUMBER: _ClassVar[int]
        CONDITION_VERSION_FIELD_NUMBER: _ClassVar[int]
        version: _revision_pb2.Revision
        resolution: _edge_pb2.Resolution
        condition_version: _revision_pb2.Revision
        def __init__(self, version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., resolution: _Optional[_Union[_edge_pb2.Resolution, str]] = ..., condition_version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
    class ResolutionEventsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: Dependencies.ResolutionEvent
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Dependencies.ResolutionEvent, _Mapping]] = ...) -> None: ...
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PREDICATE_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_EVENTS_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    edges: _containers.RepeatedCompositeFieldContainer[_edge_pb2.Edge]
    predicate: Dependencies.Group
    resolution_events: _containers.MessageMap[int, Dependencies.ResolutionEvent]
    resolution: _edge_pb2.Resolution
    def __init__(self, edges: _Optional[_Iterable[_Union[_edge_pb2.Edge, _Mapping]]] = ..., predicate: _Optional[_Union[Dependencies.Group, _Mapping]] = ..., resolution_events: _Optional[_Mapping[int, Dependencies.ResolutionEvent]] = ..., resolution: _Optional[_Union[_edge_pb2.Resolution, str]] = ...) -> None: ...
