from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllocateWorkNodeIDsResponse(_message.Message):
    __slots__ = ("ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedCompositeFieldContainer[_identifier_pb2.Stage]
    def __init__(self, ids: _Optional[_Iterable[_Union[_identifier_pb2.Stage, _Mapping]]] = ...) -> None: ...
