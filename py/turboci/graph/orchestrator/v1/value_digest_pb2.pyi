from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValueHashAlgo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_HASH_ALGO_UNKNOWN: _ClassVar[ValueHashAlgo]
    VALUE_HASH_ALGO_SHA256: _ClassVar[ValueHashAlgo]
VALUE_HASH_ALGO_UNKNOWN: ValueHashAlgo
VALUE_HASH_ALGO_SHA256: ValueHashAlgo

class ValueDigest(_message.Message):
    __slots__ = ("hash", "size_bytes", "algo")
    HASH_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    ALGO_FIELD_NUMBER: _ClassVar[int]
    hash: bytes
    size_bytes: int
    algo: ValueHashAlgo
    def __init__(self, hash: _Optional[bytes] = ..., size_bytes: _Optional[int] = ..., algo: _Optional[_Union[ValueHashAlgo, str]] = ...) -> None: ...
