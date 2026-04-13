from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransactionDetails(_message.Message):
    __slots__ = ("nodes_observed", "snapshot_version")
    NODES_OBSERVED_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_VERSION_FIELD_NUMBER: _ClassVar[int]
    nodes_observed: _containers.RepeatedCompositeFieldContainer[_identifier_pb2.Identifier]
    snapshot_version: _revision_pb2.Revision
    def __init__(self, nodes_observed: _Optional[_Iterable[_Union[_identifier_pb2.Identifier, _Mapping]]] = ..., snapshot_version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
