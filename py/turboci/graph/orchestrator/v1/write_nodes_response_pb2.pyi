from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WriteNodesResponse(_message.Message):
    __slots__ = ("written_version", "current_attempt_state")
    WRITTEN_VERSION_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
    written_version: _revision_pb2.Revision
    current_attempt_state: _stage_pb2.StageAttemptCurrentState
    def __init__(self, written_version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., current_attempt_state: _Optional[_Union[_stage_pb2.StageAttemptCurrentState, _Mapping]] = ...) -> None: ...
