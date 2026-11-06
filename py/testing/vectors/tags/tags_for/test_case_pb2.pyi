from google.protobuf import empty_pb2 as _empty_pb2
from testing.tags import demo_pb2 as _demo_pb2
from turboci.graph.orchestrator.v1 import tags_pb2 as _tags_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagsFor(_message.Message):
    __slots__ = ("input", "output")
    class Input(_message.Message):
        __slots__ = ("my", "complex", "unsupported_kind", "recursive", "recursive_untagged", "mutual_a", "mutual_b", "mutual_untagged_a", "mutual_untagged_b", "loop_a", "loop_b", "loop_c", "loop_d", "empty")
        MY_FIELD_NUMBER: _ClassVar[int]
        COMPLEX_FIELD_NUMBER: _ClassVar[int]
        UNSUPPORTED_KIND_FIELD_NUMBER: _ClassVar[int]
        RECURSIVE_FIELD_NUMBER: _ClassVar[int]
        RECURSIVE_UNTAGGED_FIELD_NUMBER: _ClassVar[int]
        MUTUAL_A_FIELD_NUMBER: _ClassVar[int]
        MUTUAL_B_FIELD_NUMBER: _ClassVar[int]
        MUTUAL_UNTAGGED_A_FIELD_NUMBER: _ClassVar[int]
        MUTUAL_UNTAGGED_B_FIELD_NUMBER: _ClassVar[int]
        LOOP_A_FIELD_NUMBER: _ClassVar[int]
        LOOP_B_FIELD_NUMBER: _ClassVar[int]
        LOOP_C_FIELD_NUMBER: _ClassVar[int]
        LOOP_D_FIELD_NUMBER: _ClassVar[int]
        EMPTY_FIELD_NUMBER: _ClassVar[int]
        my: _demo_pb2.MyMessage
        complex: _demo_pb2.ComplexMessage
        unsupported_kind: _demo_pb2.UnsupportedKindMessage
        recursive: _demo_pb2.RecursiveMessage
        recursive_untagged: _demo_pb2.RecursiveUntaggedMessage
        mutual_a: _demo_pb2.MutualMessageA
        mutual_b: _demo_pb2.MutualMessageB
        mutual_untagged_a: _demo_pb2.MutualUntaggedMessageA
        mutual_untagged_b: _demo_pb2.MutualUntaggedMessageB
        loop_a: _demo_pb2.LoopMessageA
        loop_b: _demo_pb2.LoopMessageB
        loop_c: _demo_pb2.LoopMessageC
        loop_d: _demo_pb2.LoopMessageD
        empty: _empty_pb2.Empty
        def __init__(self, my: _Optional[_Union[_demo_pb2.MyMessage, _Mapping]] = ..., complex: _Optional[_Union[_demo_pb2.ComplexMessage, _Mapping]] = ..., unsupported_kind: _Optional[_Union[_demo_pb2.UnsupportedKindMessage, _Mapping]] = ..., recursive: _Optional[_Union[_demo_pb2.RecursiveMessage, _Mapping]] = ..., recursive_untagged: _Optional[_Union[_demo_pb2.RecursiveUntaggedMessage, _Mapping]] = ..., mutual_a: _Optional[_Union[_demo_pb2.MutualMessageA, _Mapping]] = ..., mutual_b: _Optional[_Union[_demo_pb2.MutualMessageB, _Mapping]] = ..., mutual_untagged_a: _Optional[_Union[_demo_pb2.MutualUntaggedMessageA, _Mapping]] = ..., mutual_untagged_b: _Optional[_Union[_demo_pb2.MutualUntaggedMessageB, _Mapping]] = ..., loop_a: _Optional[_Union[_demo_pb2.LoopMessageA, _Mapping]] = ..., loop_b: _Optional[_Union[_demo_pb2.LoopMessageB, _Mapping]] = ..., loop_c: _Optional[_Union[_demo_pb2.LoopMessageC, _Mapping]] = ..., loop_d: _Optional[_Union[_demo_pb2.LoopMessageD, _Mapping]] = ..., empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
    class Output(_message.Message):
        __slots__ = ("error", "tag")
        ERROR_FIELD_NUMBER: _ClassVar[int]
        TAG_FIELD_NUMBER: _ClassVar[int]
        error: str
        tag: _containers.RepeatedCompositeFieldContainer[_tags_pb2.Tag]
        def __init__(self, error: _Optional[str] = ..., tag: _Optional[_Iterable[_Union[_tags_pb2.Tag, _Mapping]]] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    input: TagsFor.Input
    output: TagsFor.Output
    def __init__(self, input: _Optional[_Union[TagsFor.Input, _Mapping]] = ..., output: _Optional[_Union[TagsFor.Output, _Mapping]] = ...) -> None: ...
