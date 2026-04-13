from google.protobuf import descriptor_pb2 as _descriptor_pb2
from turboci.graph.ids.v1 import identifier_kind_pb2 as _identifier_kind_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
TURBOCI_RPC_FIELD_NUMBER: _ClassVar[int]
turboci_rpc: _descriptor.FieldDescriptor

class MethodOptions(_message.Message):
    __slots__ = ("permission",)
    class Permission(_message.Message):
        __slots__ = ("internal", "external", "in_value_realm", "potentially_conditional_on")
        INTERNAL_FIELD_NUMBER: _ClassVar[int]
        EXTERNAL_FIELD_NUMBER: _ClassVar[int]
        IN_FIELD_NUMBER: _ClassVar[int]
        IN_VALUE_REALM_FIELD_NUMBER: _ClassVar[int]
        POTENTIALLY_CONDITIONAL_ON_FIELD_NUMBER: _ClassVar[int]
        FOR_FIELD_NUMBER: _ClassVar[int]
        internal: str
        external: str
        in_value_realm: bool
        potentially_conditional_on: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, internal: _Optional[str] = ..., external: _Optional[str] = ..., in_value_realm: _Optional[bool] = ..., potentially_conditional_on: _Optional[_Iterable[str]] = ..., **kwargs) -> None: ...
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    permission: _containers.RepeatedCompositeFieldContainer[MethodOptions.Permission]
    def __init__(self, permission: _Optional[_Iterable[_Union[MethodOptions.Permission, _Mapping]]] = ...) -> None: ...
