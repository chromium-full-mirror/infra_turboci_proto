from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CancelWorkPlanResponse(_message.Message):
    __slots__ = ("cancelled_at",)
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    cancelled_at: _revision_pb2.Revision
    def __init__(self, cancelled_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
