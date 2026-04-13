from turboci.graph.orchestrator.v1 import type_set_pb2 as _type_set_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TypeInfo(_message.Message):
    __slots__ = ("wanted", "unknown_jsonpb", "known")
    WANTED_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_JSONPB_FIELD_NUMBER: _ClassVar[int]
    KNOWN_FIELD_NUMBER: _ClassVar[int]
    wanted: _type_set_pb2.TypeSet
    unknown_jsonpb: bool
    known: _type_set_pb2.TypeSet
    def __init__(self, wanted: _Optional[_Union[_type_set_pb2.TypeSet, _Mapping]] = ..., unknown_jsonpb: _Optional[bool] = ..., known: _Optional[_Union[_type_set_pb2.TypeSet, _Mapping]] = ...) -> None: ...
