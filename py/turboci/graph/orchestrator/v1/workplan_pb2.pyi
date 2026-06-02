from google.api import field_behavior_pb2 as _field_behavior_pb2
from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import check_pb2 as _check_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WorkPlan(_message.Message):
    __slots__ = ("identifier", "version", "realm", "workflow_name", "checks", "stages")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_NAME_FIELD_NUMBER: _ClassVar[int]
    CHECKS_FIELD_NUMBER: _ClassVar[int]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    identifier: _identifier_pb2.WorkPlan
    version: _revision_pb2.Revision
    realm: str
    workflow_name: str
    checks: _containers.RepeatedCompositeFieldContainer[_check_pb2.Check]
    stages: _containers.RepeatedCompositeFieldContainer[_stage_pb2.Stage]
    def __init__(self, identifier: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., realm: _Optional[str] = ..., workflow_name: _Optional[str] = ..., checks: _Optional[_Iterable[_Union[_check_pb2.Check, _Mapping]]] = ..., stages: _Optional[_Iterable[_Union[_stage_pb2.Stage, _Mapping]]] = ...) -> None: ...
