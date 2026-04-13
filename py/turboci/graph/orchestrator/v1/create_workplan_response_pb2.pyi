from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateWorkPlanResponse(_message.Message):
    __slots__ = ("identifier", "creator_token")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    CREATOR_TOKEN_FIELD_NUMBER: _ClassVar[int]
    identifier: _identifier_pb2.WorkPlan
    creator_token: str
    def __init__(self, identifier: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., creator_token: _Optional[str] = ...) -> None: ...
