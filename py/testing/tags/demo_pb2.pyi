from turboci import tag_pb2 as _tag_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEST_ENUM_UNKNOWN: _ClassVar[TestEnum]
    TEST_ENUM_ONE: _ClassVar[TestEnum]
    TEST_ENUM_TWO: _ClassVar[TestEnum]
TEST_ENUM_UNKNOWN: TestEnum
TEST_ENUM_ONE: TestEnum
TEST_ENUM_TWO: TestEnum

class MyMessage(_message.Message):
    __slots__ = ("tagged_field", "untagged_field")
    TAGGED_FIELD_FIELD_NUMBER: _ClassVar[int]
    UNTAGGED_FIELD_FIELD_NUMBER: _ClassVar[int]
    tagged_field: str
    untagged_field: str
    def __init__(self, tagged_field: _Optional[str] = ..., untagged_field: _Optional[str] = ...) -> None: ...

class ComplexMessage(_message.Message):
    __slots__ = ("local_str", "workplan_str", "global_str", "local_bool", "local_enum", "rep_str", "map_sub", "rep_sub", "sub", "split_index", "explicit_presence_bool")
    class SubMessage(_message.Message):
        __slots__ = ("sub_tagged",)
        SUB_TAGGED_FIELD_NUMBER: _ClassVar[int]
        sub_tagged: str
        def __init__(self, sub_tagged: _Optional[str] = ...) -> None: ...
    class MapSubEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ComplexMessage.SubMessage
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ComplexMessage.SubMessage, _Mapping]] = ...) -> None: ...
    LOCAL_STR_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_STR_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_STR_FIELD_NUMBER: _ClassVar[int]
    LOCAL_BOOL_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ENUM_FIELD_NUMBER: _ClassVar[int]
    REP_STR_FIELD_NUMBER: _ClassVar[int]
    MAP_SUB_FIELD_NUMBER: _ClassVar[int]
    REP_SUB_FIELD_NUMBER: _ClassVar[int]
    SUB_FIELD_NUMBER: _ClassVar[int]
    SPLIT_INDEX_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_PRESENCE_BOOL_FIELD_NUMBER: _ClassVar[int]
    local_str: str
    workplan_str: str
    global_str: str
    local_bool: bool
    local_enum: TestEnum
    rep_str: _containers.RepeatedScalarFieldContainer[str]
    map_sub: _containers.MessageMap[str, ComplexMessage.SubMessage]
    rep_sub: _containers.RepeatedCompositeFieldContainer[ComplexMessage.SubMessage]
    sub: ComplexMessage.SubMessage
    split_index: int
    explicit_presence_bool: bool
    def __init__(self, local_str: _Optional[str] = ..., workplan_str: _Optional[str] = ..., global_str: _Optional[str] = ..., local_bool: _Optional[bool] = ..., local_enum: _Optional[_Union[TestEnum, str]] = ..., rep_str: _Optional[_Iterable[str]] = ..., map_sub: _Optional[_Mapping[str, ComplexMessage.SubMessage]] = ..., rep_sub: _Optional[_Iterable[_Union[ComplexMessage.SubMessage, _Mapping]]] = ..., sub: _Optional[_Union[ComplexMessage.SubMessage, _Mapping]] = ..., split_index: _Optional[int] = ..., explicit_presence_bool: _Optional[bool] = ...) -> None: ...

class UnsupportedKindMessage(_message.Message):
    __slots__ = ("bad_field",)
    BAD_FIELD_FIELD_NUMBER: _ClassVar[int]
    bad_field: bytes
    def __init__(self, bad_field: _Optional[bytes] = ...) -> None: ...

class RecursiveMessage(_message.Message):
    __slots__ = ("deeper", "tagged")
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    TAGGED_FIELD_NUMBER: _ClassVar[int]
    deeper: RecursiveMessage
    tagged: str
    def __init__(self, deeper: _Optional[_Union[RecursiveMessage, _Mapping]] = ..., tagged: _Optional[str] = ...) -> None: ...

class RecursiveUntaggedMessage(_message.Message):
    __slots__ = ("deeper", "untagged")
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    UNTAGGED_FIELD_NUMBER: _ClassVar[int]
    deeper: RecursiveUntaggedMessage
    untagged: str
    def __init__(self, deeper: _Optional[_Union[RecursiveUntaggedMessage, _Mapping]] = ..., untagged: _Optional[str] = ...) -> None: ...

class MutualMessageA(_message.Message):
    __slots__ = ("deeper",)
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    deeper: MutualMessageB
    def __init__(self, deeper: _Optional[_Union[MutualMessageB, _Mapping]] = ...) -> None: ...

class MutualMessageB(_message.Message):
    __slots__ = ("deeper", "tagged")
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    TAGGED_FIELD_NUMBER: _ClassVar[int]
    deeper: MutualMessageA
    tagged: str
    def __init__(self, deeper: _Optional[_Union[MutualMessageA, _Mapping]] = ..., tagged: _Optional[str] = ...) -> None: ...

class MutualUntaggedMessageA(_message.Message):
    __slots__ = ("deeper",)
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    deeper: MutualUntaggedMessageB
    def __init__(self, deeper: _Optional[_Union[MutualUntaggedMessageB, _Mapping]] = ...) -> None: ...

class MutualUntaggedMessageB(_message.Message):
    __slots__ = ("deeper", "untagged")
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    UNTAGGED_FIELD_NUMBER: _ClassVar[int]
    deeper: MutualUntaggedMessageA
    untagged: str
    def __init__(self, deeper: _Optional[_Union[MutualUntaggedMessageA, _Mapping]] = ..., untagged: _Optional[str] = ...) -> None: ...

class LoopMessageA(_message.Message):
    __slots__ = ("deeper",)
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    deeper: LoopMessageB
    def __init__(self, deeper: _Optional[_Union[LoopMessageB, _Mapping]] = ...) -> None: ...

class LoopMessageB(_message.Message):
    __slots__ = ("deeper",)
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    deeper: LoopMessageC
    def __init__(self, deeper: _Optional[_Union[LoopMessageC, _Mapping]] = ...) -> None: ...

class LoopMessageC(_message.Message):
    __slots__ = ("deeper",)
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    deeper: LoopMessageD
    def __init__(self, deeper: _Optional[_Union[LoopMessageD, _Mapping]] = ...) -> None: ...

class LoopMessageD(_message.Message):
    __slots__ = ("deeper", "tagged")
    DEEPER_FIELD_NUMBER: _ClassVar[int]
    TAGGED_FIELD_NUMBER: _ClassVar[int]
    deeper: LoopMessageA
    tagged: str
    def __init__(self, deeper: _Optional[_Union[LoopMessageA, _Mapping]] = ..., tagged: _Optional[str] = ...) -> None: ...
