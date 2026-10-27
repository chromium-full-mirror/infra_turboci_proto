from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tag(_message.Message):
    __slots__ = ("key", "indexed", "values")
    class Value(_message.Message):
        __slots__ = ("indexed", "duplicate_count", "str_value", "bool_value", "int_value")
        INDEXED_FIELD_NUMBER: _ClassVar[int]
        DUPLICATE_COUNT_FIELD_NUMBER: _ClassVar[int]
        STR_VALUE_FIELD_NUMBER: _ClassVar[int]
        BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
        INT_VALUE_FIELD_NUMBER: _ClassVar[int]
        indexed: bool
        duplicate_count: int
        str_value: str
        bool_value: bool
        int_value: int
        def __init__(self, indexed: _Optional[bool] = ..., duplicate_count: _Optional[int] = ..., str_value: _Optional[str] = ..., bool_value: _Optional[bool] = ..., int_value: _Optional[int] = ...) -> None: ...
    KEY_FIELD_NUMBER: _ClassVar[int]
    INDEXED_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    key: str
    indexed: bool
    values: _containers.RepeatedCompositeFieldContainer[Tag.Value]
    def __init__(self, key: _Optional[str] = ..., indexed: _Optional[bool] = ..., values: _Optional[_Iterable[_Union[Tag.Value, _Mapping]]] = ...) -> None: ...
