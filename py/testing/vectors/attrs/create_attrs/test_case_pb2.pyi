from turboci.graph.orchestrator.v1 import attribute_pb2 as _attribute_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from turboci.graph.orchestrator.v1 import write_nodes_request_pb2 as _write_nodes_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAttrs(_message.Message):
    __slots__ = ("input", "output", "err")
    class ForStage(_message.Message):
        __slots__ = ("name", "expression", "on_state", "attribute_type", "indexed")
        NAME_FIELD_NUMBER: _ClassVar[int]
        EXPRESSION_FIELD_NUMBER: _ClassVar[int]
        ON_STATE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
        INDEXED_FIELD_NUMBER: _ClassVar[int]
        name: str
        expression: str
        on_state: _stage_state_pb2.StageState
        attribute_type: _attribute_pb2.AttributeType
        indexed: bool
        def __init__(self, name: _Optional[str] = ..., expression: _Optional[str] = ..., on_state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., attribute_type: _Optional[_Union[_attribute_pb2.AttributeType, str]] = ..., indexed: _Optional[bool] = ...) -> None: ...
    class ForCheck(_message.Message):
        __slots__ = ("name", "expression", "on_state", "attribute_type", "indexed")
        NAME_FIELD_NUMBER: _ClassVar[int]
        EXPRESSION_FIELD_NUMBER: _ClassVar[int]
        ON_STATE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
        INDEXED_FIELD_NUMBER: _ClassVar[int]
        name: str
        expression: str
        on_state: _check_state_pb2.CheckState
        attribute_type: _attribute_pb2.AttributeType
        indexed: bool
        def __init__(self, name: _Optional[str] = ..., expression: _Optional[str] = ..., on_state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., attribute_type: _Optional[_Union[_attribute_pb2.AttributeType, str]] = ..., indexed: _Optional[bool] = ...) -> None: ...
    class AddStageAttributes(_message.Message):
        __slots__ = ("stage_write", "attributes")
        STAGE_WRITE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        stage_write: _write_nodes_request_pb2.WriteNodesRequest.StageWrite
        attributes: _containers.RepeatedCompositeFieldContainer[_write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite]
        def __init__(self, stage_write: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.StageWrite, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[_write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite, _Mapping]]] = ...) -> None: ...
    class AddCheckAttributes(_message.Message):
        __slots__ = ("check_write", "attributes")
        CHECK_WRITE_FIELD_NUMBER: _ClassVar[int]
        ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        check_write: _write_nodes_request_pb2.WriteNodesRequest.CheckWrite
        attributes: _containers.RepeatedCompositeFieldContainer[_write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite]
        def __init__(self, check_write: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.CheckWrite, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[_write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite, _Mapping]]] = ...) -> None: ...
    class Input(_message.Message):
        __slots__ = ("for_stage", "for_check", "add_stage_attributes", "add_check_attributes")
        FOR_STAGE_FIELD_NUMBER: _ClassVar[int]
        FOR_CHECK_FIELD_NUMBER: _ClassVar[int]
        ADD_STAGE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        ADD_CHECK_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
        for_stage: CreateAttrs.ForStage
        for_check: CreateAttrs.ForCheck
        add_stage_attributes: CreateAttrs.AddStageAttributes
        add_check_attributes: CreateAttrs.AddCheckAttributes
        def __init__(self, for_stage: _Optional[_Union[CreateAttrs.ForStage, _Mapping]] = ..., for_check: _Optional[_Union[CreateAttrs.ForCheck, _Mapping]] = ..., add_stage_attributes: _Optional[_Union[CreateAttrs.AddStageAttributes, _Mapping]] = ..., add_check_attributes: _Optional[_Union[CreateAttrs.AddCheckAttributes, _Mapping]] = ...) -> None: ...
    class Output(_message.Message):
        __slots__ = ("stage_attribute", "check_attribute", "stage_write", "check_write")
        STAGE_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
        CHECK_ATTRIBUTE_FIELD_NUMBER: _ClassVar[int]
        STAGE_WRITE_FIELD_NUMBER: _ClassVar[int]
        CHECK_WRITE_FIELD_NUMBER: _ClassVar[int]
        stage_attribute: _write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite
        check_attribute: _write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite
        stage_write: _write_nodes_request_pb2.WriteNodesRequest.StageWrite
        check_write: _write_nodes_request_pb2.WriteNodesRequest.CheckWrite
        def __init__(self, stage_attribute: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.StageAttributeWrite, _Mapping]] = ..., check_attribute: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.CheckAttributeWrite, _Mapping]] = ..., stage_write: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.StageWrite, _Mapping]] = ..., check_write: _Optional[_Union[_write_nodes_request_pb2.WriteNodesRequest.CheckWrite, _Mapping]] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    ERR_FIELD_NUMBER: _ClassVar[int]
    input: CreateAttrs.Input
    output: CreateAttrs.Output
    err: str
    def __init__(self, input: _Optional[_Union[CreateAttrs.Input, _Mapping]] = ..., output: _Optional[_Union[CreateAttrs.Output, _Mapping]] = ..., err: _Optional[str] = ...) -> None: ...
