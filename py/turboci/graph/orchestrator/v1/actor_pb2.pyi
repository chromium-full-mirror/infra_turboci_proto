from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Actor(_message.Message):
    __slots__ = ("stage_attempt", "orchestrator", "workplan_creator", "external", "legacy_workplan_user")
    class Orchestrator(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class WorkplanCreator(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class External(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class LegacyWorkplanUser(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    STAGE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    ORCHESTRATOR_FIELD_NUMBER: _ClassVar[int]
    WORKPLAN_CREATOR_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_FIELD_NUMBER: _ClassVar[int]
    LEGACY_WORKPLAN_USER_FIELD_NUMBER: _ClassVar[int]
    stage_attempt: _identifier_pb2.StageAttempt
    orchestrator: Actor.Orchestrator
    workplan_creator: Actor.WorkplanCreator
    external: Actor.External
    legacy_workplan_user: Actor.LegacyWorkplanUser
    def __init__(self, stage_attempt: _Optional[_Union[_identifier_pb2.StageAttempt, _Mapping]] = ..., orchestrator: _Optional[_Union[Actor.Orchestrator, _Mapping]] = ..., workplan_creator: _Optional[_Union[Actor.WorkplanCreator, _Mapping]] = ..., external: _Optional[_Union[Actor.External, _Mapping]] = ..., legacy_workplan_user: _Optional[_Union[Actor.LegacyWorkplanUser, _Mapping]] = ...) -> None: ...
