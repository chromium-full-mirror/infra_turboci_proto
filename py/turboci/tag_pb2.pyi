from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_REF: _ClassVar[ReadScope]
    NODE: _ClassVar[ReadScope]
    WORK_PLAN: _ClassVar[ReadScope]
VALUE_REF: ReadScope
NODE: ReadScope
WORK_PLAN: ReadScope
TAG_FIELD_NUMBER: _ClassVar[int]
tag: _descriptor.FieldDescriptor

class Tag(_message.Message):
    __slots__ = ("key_scope", "value_scope", "alt_key", "index_unset")
    KEY_SCOPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_SCOPE_FIELD_NUMBER: _ClassVar[int]
    ALT_KEY_FIELD_NUMBER: _ClassVar[int]
    INDEX_UNSET_FIELD_NUMBER: _ClassVar[int]
    key_scope: ReadScope
    value_scope: ReadScope
    alt_key: _containers.RepeatedScalarFieldContainer[str]
    index_unset: bool
    def __init__(self, key_scope: _Optional[_Union[ReadScope, str]] = ..., value_scope: _Optional[_Union[ReadScope, str]] = ..., alt_key: _Optional[_Iterable[str]] = ..., index_unset: _Optional[bool] = ...) -> None: ...
