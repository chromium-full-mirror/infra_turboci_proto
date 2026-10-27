from turboci.graph.orchestrator.v1 import check_kind_pb2 as _check_kind_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import stage_concluded_reason_pb2 as _stage_concluded_reason_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from turboci.graph.orchestrator.v1 import value_slot_pb2 as _value_slot_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodePredicate(_message.Message):
    __slots__ = ("condition", "all", "any")
    class Condition(_message.Message):
        __slots__ = ("stage", "check", "value_type", "tag", "attribute")
        class StageCondition(_message.Message):
            __slots__ = ("state", "args_type_url", "sub_type", "concluded_reason", "work_executor_type")
            STATE_FIELD_NUMBER: _ClassVar[int]
            ARGS_TYPE_URL_FIELD_NUMBER: _ClassVar[int]
            SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
            CONCLUDED_REASON_FIELD_NUMBER: _ClassVar[int]
            WORK_EXECUTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
            state: _containers.RepeatedScalarFieldContainer[_stage_state_pb2.StageState]
            args_type_url: _containers.RepeatedScalarFieldContainer[str]
            sub_type: _containers.RepeatedScalarFieldContainer[str]
            concluded_reason: _containers.RepeatedScalarFieldContainer[_stage_concluded_reason_pb2.StageConcludedReason]
            work_executor_type: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, state: _Optional[_Iterable[_Union[_stage_state_pb2.StageState, str]]] = ..., args_type_url: _Optional[_Iterable[str]] = ..., sub_type: _Optional[_Iterable[str]] = ..., concluded_reason: _Optional[_Iterable[_Union[_stage_concluded_reason_pb2.StageConcludedReason, str]]] = ..., work_executor_type: _Optional[_Iterable[int]] = ...) -> None: ...
        class CheckCondition(_message.Message):
            __slots__ = ("state", "kind", "sub_type")
            STATE_FIELD_NUMBER: _ClassVar[int]
            KIND_FIELD_NUMBER: _ClassVar[int]
            SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
            state: _containers.RepeatedScalarFieldContainer[_check_state_pb2.CheckState]
            kind: _containers.RepeatedScalarFieldContainer[_check_kind_pb2.CheckKind]
            sub_type: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, state: _Optional[_Iterable[_Union[_check_state_pb2.CheckState, str]]] = ..., kind: _Optional[_Iterable[_Union[_check_kind_pb2.CheckKind, str]]] = ..., sub_type: _Optional[_Iterable[str]] = ...) -> None: ...
        class ValueTypeCondition(_message.Message):
            __slots__ = ("type_url", "slot")
            TYPE_URL_FIELD_NUMBER: _ClassVar[int]
            SLOT_FIELD_NUMBER: _ClassVar[int]
            type_url: str
            slot: _containers.RepeatedScalarFieldContainer[_value_slot_pb2.ValueSlot]
            def __init__(self, type_url: _Optional[str] = ..., slot: _Optional[_Iterable[_Union[_value_slot_pb2.ValueSlot, str]]] = ...) -> None: ...
        class TagCondition(_message.Message):
            __slots__ = ("key", "str_value", "bool_value", "int_value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            STR_VALUE_FIELD_NUMBER: _ClassVar[int]
            BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
            INT_VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            str_value: str
            bool_value: bool
            int_value: int
            def __init__(self, key: _Optional[str] = ..., str_value: _Optional[str] = ..., bool_value: _Optional[bool] = ..., int_value: _Optional[int] = ...) -> None: ...
        class AttributeCondition(_message.Message):
            __slots__ = ("name", "str_value", "bool_value", "int_value")
            NAME_FIELD_NUMBER: _ClassVar[int]
            STR_VALUE_FIELD_NUMBER: _ClassVar[int]
            BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
            INT_VALUE_FIELD_NUMBER: _ClassVar[int]
            name: str
            str_value: str
            bool_value: bool
            int_value: int
            def __init__(self, name: _Optional[str] = ..., str_value: _Optional[str] = ..., bool_value: _Optional[bool] = ..., int_value: _Optional[int] = ...) -> None: ...
        STAGE_FIELD_NUMBER: _ClassVar[int]
        CHECK_FIELD_NUMBER: _ClassVar[int]
        VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
        TAG_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
        stage: NodePredicate.Condition.StageCondition
        check: NodePredicate.Condition.CheckCondition
        value_type: _containers.RepeatedCompositeFieldContainer[NodePredicate.Condition.ValueTypeCondition]
        tag: _containers.RepeatedCompositeFieldContainer[NodePredicate.Condition.TagCondition]
        attribute: NodePredicate.Condition.AttributeCondition
        def __init__(self, stage: _Optional[_Union[NodePredicate.Condition.StageCondition, _Mapping]] = ..., check: _Optional[_Union[NodePredicate.Condition.CheckCondition, _Mapping]] = ..., value_type: _Optional[_Iterable[_Union[NodePredicate.Condition.ValueTypeCondition, _Mapping]]] = ..., tag: _Optional[_Iterable[_Union[NodePredicate.Condition.TagCondition, _Mapping]]] = ..., attribute: _Optional[_Union[NodePredicate.Condition.AttributeCondition, _Mapping]] = ...) -> None: ...
    class Terms(_message.Message):
        __slots__ = ("terms",)
        TERMS_FIELD_NUMBER: _ClassVar[int]
        terms: _containers.RepeatedCompositeFieldContainer[NodePredicate]
        def __init__(self, terms: _Optional[_Iterable[_Union[NodePredicate, _Mapping]]] = ...) -> None: ...
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    ANY_FIELD_NUMBER: _ClassVar[int]
    condition: NodePredicate.Condition
    all: NodePredicate.Terms
    any: NodePredicate.Terms
    def __init__(self, condition: _Optional[_Union[NodePredicate.Condition, _Mapping]] = ..., all: _Optional[_Union[NodePredicate.Terms, _Mapping]] = ..., any: _Optional[_Union[NodePredicate.Terms, _Mapping]] = ...) -> None: ...
