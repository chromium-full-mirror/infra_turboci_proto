from google.protobuf import descriptor_pb2 as _descriptor_pb2
from turboci.graph.ids.v1 import identifier_kind_pb2 as _identifier_kind_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
TURBOCI_FIELD_NUMBER: _ClassVar[int]
turboci: _descriptor.FieldDescriptor

class FieldOptions(_message.Message):
    __slots__ = ("check", "id", "creation_only", "realm_inherits_writer")
    class CheckFieldOptions(_message.Message):
        __slots__ = ("editable",)
        EDITABLE_FIELD_NUMBER: _ClassVar[int]
        editable: _containers.RepeatedScalarFieldContainer[_check_state_pb2.CheckState]
        def __init__(self, editable: _Optional[_Iterable[_Union[_check_state_pb2.CheckState, str]]] = ...) -> None: ...
    class IdentifierOptions(_message.Message):
        __slots__ = ("allowed",)
        ALLOWED_FIELD_NUMBER: _ClassVar[int]
        allowed: _containers.RepeatedScalarFieldContainer[_identifier_kind_pb2.IdentifierKind]
        def __init__(self, allowed: _Optional[_Iterable[_Union[_identifier_kind_pb2.IdentifierKind, str]]] = ...) -> None: ...
    CHECK_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATION_ONLY_FIELD_NUMBER: _ClassVar[int]
    REALM_INHERITS_WRITER_FIELD_NUMBER: _ClassVar[int]
    check: FieldOptions.CheckFieldOptions
    id: FieldOptions.IdentifierOptions
    creation_only: bool
    realm_inherits_writer: bool
    def __init__(self, check: _Optional[_Union[FieldOptions.CheckFieldOptions, _Mapping]] = ..., id: _Optional[_Union[FieldOptions.IdentifierOptions, _Mapping]] = ..., creation_only: _Optional[bool] = ..., realm_inherits_writer: _Optional[bool] = ...) -> None: ...
