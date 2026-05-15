from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2 as _value_write_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CancelWorkPlanRequest(_message.Message):
    __slots__ = ("token", "workplan_id", "reason")
    class Reason(_message.Message):
        __slots__ = ("message", "details")
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        message: str
        details: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        def __init__(self, message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ...) -> None: ...
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    token: str
    workplan_id: _identifier_pb2.WorkPlan
    reason: CancelWorkPlanRequest.Reason
    def __init__(self, token: _Optional[str] = ..., workplan_id: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., reason: _Optional[_Union[CancelWorkPlanRequest.Reason, _Mapping]] = ...) -> None: ...
