from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.ids.v1 import identifier_kind_pb2 as _identifier_kind_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ToFromString(_message.Message):
    __slots__ = ("input", "output")
    class Output(_message.Message):
        __slots__ = ("err", "parsed", "kind", "root")
        class Root(_message.Message):
            __slots__ = ("work_plan", "check", "stage")
            WORK_PLAN_FIELD_NUMBER: _ClassVar[int]
            CHECK_FIELD_NUMBER: _ClassVar[int]
            STAGE_FIELD_NUMBER: _ClassVar[int]
            work_plan: _identifier_pb2.WorkPlan
            check: _identifier_pb2.Check
            stage: _identifier_pb2.Stage
            def __init__(self, work_plan: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., check: _Optional[_Union[_identifier_pb2.Check, _Mapping]] = ..., stage: _Optional[_Union[_identifier_pb2.Stage, _Mapping]] = ...) -> None: ...
        ERR_FIELD_NUMBER: _ClassVar[int]
        PARSED_FIELD_NUMBER: _ClassVar[int]
        KIND_FIELD_NUMBER: _ClassVar[int]
        ROOT_FIELD_NUMBER: _ClassVar[int]
        err: bool
        parsed: _identifier_pb2.Identifier
        kind: _identifier_kind_pb2.IdentifierKind
        root: ToFromString.Output.Root
        def __init__(self, err: _Optional[bool] = ..., parsed: _Optional[_Union[_identifier_pb2.Identifier, _Mapping]] = ..., kind: _Optional[_Union[_identifier_kind_pb2.IdentifierKind, str]] = ..., root: _Optional[_Union[ToFromString.Output.Root, _Mapping]] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    input: str
    output: ToFromString.Output
    def __init__(self, input: _Optional[str] = ..., output: _Optional[_Union[ToFromString.Output, _Mapping]] = ...) -> None: ...
