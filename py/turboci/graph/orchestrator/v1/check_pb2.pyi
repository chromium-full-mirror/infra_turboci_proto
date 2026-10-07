from google.api import field_behavior_pb2 as _field_behavior_pb2
from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import actor_pb2 as _actor_pb2
from turboci.graph.orchestrator.v1 import attribute_pb2 as _attribute_pb2
from turboci.graph.orchestrator.v1 import check_kind_pb2 as _check_kind_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import dependencies_pb2 as _dependencies_pb2
from turboci.graph.orchestrator.v1 import edit_pb2 as _edit_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2 as _stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Check(_message.Message):
    __slots__ = ("identifier", "display_name", "created_by", "kind", "sub_type", "realm", "version", "state", "state_history", "dependencies", "options", "results", "edits", "attributes")
    class StateHistoryEntry(_message.Message):
        __slots__ = ("state", "version")
        STATE_FIELD_NUMBER: _ClassVar[int]
        VERSION_FIELD_NUMBER: _ClassVar[int]
        state: _check_state_pb2.CheckState
        version: _revision_pb2.Revision
        def __init__(self, state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
    class Result(_message.Message):
        __slots__ = ("identifier", "owner", "created_at", "data", "finalized_at", "attempt_state")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        OWNER_FIELD_NUMBER: _ClassVar[int]
        CREATED_AT_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        FINALIZED_AT_FIELD_NUMBER: _ClassVar[int]
        ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.CheckResult
        owner: _actor_pb2.Actor
        created_at: _revision_pb2.Revision
        data: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
        finalized_at: _revision_pb2.Revision
        attempt_state: _stage_attempt_state_pb2.StageAttemptState
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.CheckResult, _Mapping]] = ..., owner: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., created_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., data: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., finalized_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., attempt_state: _Optional[_Union[_stage_attempt_state_pb2.StageAttemptState, str]] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    EDITS_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    identifier: _identifier_pb2.Check
    display_name: str
    created_by: _actor_pb2.Actor
    kind: _check_kind_pb2.CheckKind
    sub_type: str
    realm: str
    version: _revision_pb2.Revision
    state: _check_state_pb2.CheckState
    state_history: _containers.RepeatedCompositeFieldContainer[Check.StateHistoryEntry]
    dependencies: _dependencies_pb2.Dependencies
    options: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
    results: _containers.RepeatedCompositeFieldContainer[Check.Result]
    edits: _containers.RepeatedCompositeFieldContainer[_edit_pb2.Edit]
    attributes: _containers.RepeatedCompositeFieldContainer[_attribute_pb2.Attribute]
    def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Check, _Mapping]] = ..., display_name: _Optional[str] = ..., created_by: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., kind: _Optional[_Union[_check_kind_pb2.CheckKind, str]] = ..., sub_type: _Optional[str] = ..., realm: _Optional[str] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., state_history: _Optional[_Iterable[_Union[Check.StateHistoryEntry, _Mapping]]] = ..., dependencies: _Optional[_Union[_dependencies_pb2.Dependencies, _Mapping]] = ..., options: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[Check.Result, _Mapping]]] = ..., edits: _Optional[_Iterable[_Union[_edit_pb2.Edit, _Mapping]]] = ..., attributes: _Optional[_Iterable[_Union[_attribute_pb2.Attribute, _Mapping]]] = ...) -> None: ...
