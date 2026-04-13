from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AllocateWorkNodeIDsRequest(_message.Message):
    __slots__ = ("token", "workplan_id", "count")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    token: str
    workplan_id: _identifier_pb2.WorkPlan
    count: int
    def __init__(self, token: _Optional[str] = ..., workplan_id: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., count: _Optional[int] = ...) -> None: ...
