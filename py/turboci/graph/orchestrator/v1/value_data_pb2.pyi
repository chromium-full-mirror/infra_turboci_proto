from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataConversionFailure(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DATA_CONVERSION_FAILURE_UNKNOWN: _ClassVar[DataConversionFailure]
    DATA_CONVERSION_FAILURE_NO_DESCRIPTOR: _ClassVar[DataConversionFailure]
    DATA_CONVERSION_FAILURE_ERROR: _ClassVar[DataConversionFailure]
DATA_CONVERSION_FAILURE_UNKNOWN: DataConversionFailure
DATA_CONVERSION_FAILURE_NO_DESCRIPTOR: DataConversionFailure
DATA_CONVERSION_FAILURE_ERROR: DataConversionFailure

class ValueData(_message.Message):
    __slots__ = ("binary", "json", "conversion_failure")
    class JsonAny(_message.Message):
        __slots__ = ("type_url", "value", "has_unknown_fields")
        TYPE_URL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        HAS_UNKNOWN_FIELDS_FIELD_NUMBER: _ClassVar[int]
        type_url: str
        value: str
        has_unknown_fields: bool
        def __init__(self, type_url: _Optional[str] = ..., value: _Optional[str] = ..., has_unknown_fields: _Optional[bool] = ...) -> None: ...
    BINARY_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_FAILURE_FIELD_NUMBER: _ClassVar[int]
    binary: _any_pb2.Any
    json: ValueData.JsonAny
    conversion_failure: DataConversionFailure
    def __init__(self, binary: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., json: _Optional[_Union[ValueData.JsonAny, _Mapping]] = ..., conversion_failure: _Optional[_Union[DataConversionFailure, str]] = ...) -> None: ...
