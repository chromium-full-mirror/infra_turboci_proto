from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import actor_pb2 as _actor_pb2
from turboci.graph.orchestrator.v1 import check_pb2 as _check_pb2
from turboci.graph.orchestrator.v1 import edit_pb2 as _edit_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2 as _value_slot_pb2
from turboci.graph.orchestrator.v1 import workplan_pb2 as _workplan_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RefsIn(_message.Message):
    __slots__ = ("input", "output", "err")
    class Input(_message.Message):
        __slots__ = ("stage", "stage_attempt", "check", "workplan", "edit")
        STAGE_FIELD_NUMBER: _ClassVar[int]
        STAGE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
        CHECK_FIELD_NUMBER: _ClassVar[int]
        WORKPLAN_FIELD_NUMBER: _ClassVar[int]
        EDIT_FIELD_NUMBER: _ClassVar[int]
        stage: _stage_pb2.Stage
        stage_attempt: _stage_pb2.Stage.Attempt
        check: _check_pb2.Check
        workplan: _workplan_pb2.WorkPlan
        edit: _edit_pb2.Edit
        def __init__(self, stage: _Optional[_Union[_stage_pb2.Stage, _Mapping]] = ..., stage_attempt: _Optional[_Union[_stage_pb2.Stage.Attempt, _Mapping]] = ..., check: _Optional[_Union[_check_pb2.Check, _Mapping]] = ..., workplan: _Optional[_Union[_workplan_pb2.WorkPlan, _Mapping]] = ..., edit: _Optional[_Union[_edit_pb2.Edit, _Mapping]] = ...) -> None: ...
    class Output(_message.Message):
        __slots__ = ("refs",)
        class ValueRefAndContext(_message.Message):
            __slots__ = ("slot", "id", "result_data", "ref")
            class ResultData(_message.Message):
                __slots__ = ("idx", "actor")
                IDX_FIELD_NUMBER: _ClassVar[int]
                ACTOR_FIELD_NUMBER: _ClassVar[int]
                idx: int
                actor: _actor_pb2.Actor
                def __init__(self, idx: _Optional[int] = ..., actor: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ...) -> None: ...
            SLOT_FIELD_NUMBER: _ClassVar[int]
            ID_FIELD_NUMBER: _ClassVar[int]
            RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
            REF_FIELD_NUMBER: _ClassVar[int]
            slot: _value_slot_pb2.ValueSlot
            id: _identifier_pb2.Identifier
            result_data: RefsIn.Output.ValueRefAndContext.ResultData
            ref: _value_ref_pb2.ValueRef
            def __init__(self, slot: _Optional[_Union[_value_slot_pb2.ValueSlot, str]] = ..., id: _Optional[_Union[_identifier_pb2.Identifier, _Mapping]] = ..., result_data: _Optional[_Union[RefsIn.Output.ValueRefAndContext.ResultData, _Mapping]] = ..., ref: _Optional[_Union[_value_ref_pb2.ValueRef, _Mapping]] = ...) -> None: ...
        REFS_FIELD_NUMBER: _ClassVar[int]
        refs: _containers.RepeatedCompositeFieldContainer[RefsIn.Output.ValueRefAndContext]
        def __init__(self, refs: _Optional[_Iterable[_Union[RefsIn.Output.ValueRefAndContext, _Mapping]]] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    input: RefsIn.Input
    output: RefsIn.Output
    err: str
    def __init__(self, input: _Optional[_Union[RefsIn.Input, _Mapping]] = ..., output: _Optional[_Union[RefsIn.Output, _Mapping]] = ..., err: _Optional[str] = ...) -> None: ...
