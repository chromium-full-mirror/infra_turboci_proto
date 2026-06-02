import datetime

from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import actor_pb2 as _actor_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import dependencies_pb2 as _dependencies_pb2
from turboci.graph.orchestrator.v1 import edit_pb2 as _edit_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_execution_policy_pb2 as _stage_attempt_execution_policy_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_state_pb2 as _stage_attempt_state_pb2
from turboci.graph.orchestrator.v1 import stage_concluded_reason_pb2 as _stage_concluded_reason_pb2
from turboci.graph.orchestrator.v1 import stage_execution_policy_pb2 as _stage_execution_policy_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Stage(_message.Message):
    __slots__ = ("identifier", "display_name", "created_by", "realm", "args", "sub_type", "version", "state", "cancelled_by", "cancelled_at", "legacy", "state_history", "dependencies", "execution_policy", "attempts", "assignments", "continuation_group", "concluded_reason", "edits")
    class Legacy(_message.Message):
        __slots__ = ("worknode", "work_executor_type")
        WORKNODE_FIELD_NUMBER: _ClassVar[int]
        WORK_EXECUTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
        worknode: _value_ref_pb2.ValueRef
        work_executor_type: int
        def __init__(self, worknode: _Optional[_Union[_value_ref_pb2.ValueRef, _Mapping]] = ..., work_executor_type: _Optional[int] = ...) -> None: ...
    class StateHistoryEntry(_message.Message):
        __slots__ = ("state", "version")
        STATE_FIELD_NUMBER: _ClassVar[int]
        VERSION_FIELD_NUMBER: _ClassVar[int]
        state: _stage_state_pb2.StageState
        version: _revision_pb2.Revision
        def __init__(self, state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
    class ExecutionPolicyState(_message.Message):
        __slots__ = ("requested", "validated")
        REQUESTED_FIELD_NUMBER: _ClassVar[int]
        VALIDATED_FIELD_NUMBER: _ClassVar[int]
        requested: _stage_execution_policy_pb2.StageExecutionPolicy
        validated: _stage_execution_policy_pb2.StageExecutionPolicy
        def __init__(self, requested: _Optional[_Union[_stage_execution_policy_pb2.StageExecutionPolicy, _Mapping]] = ..., validated: _Optional[_Union[_stage_execution_policy_pb2.StageExecutionPolicy, _Mapping]] = ...) -> None: ...
    class Attempt(_message.Message):
        __slots__ = ("identifier", "version", "last_heartbeat", "state", "state_history", "waiting_until", "process_uid", "details", "progress", "execution_policy")
        class StateHistoryEntry(_message.Message):
            __slots__ = ("state", "version")
            STATE_FIELD_NUMBER: _ClassVar[int]
            VERSION_FIELD_NUMBER: _ClassVar[int]
            state: _stage_attempt_state_pb2.StageAttemptState
            version: _revision_pb2.Revision
            def __init__(self, state: _Optional[_Union[_stage_attempt_state_pb2.StageAttemptState, str]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
        class Progress(_message.Message):
            __slots__ = ("message", "version", "details", "created_by", "idempotency_key")
            MESSAGE_FIELD_NUMBER: _ClassVar[int]
            VERSION_FIELD_NUMBER: _ClassVar[int]
            DETAILS_FIELD_NUMBER: _ClassVar[int]
            CREATED_BY_FIELD_NUMBER: _ClassVar[int]
            IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
            message: str
            version: _revision_pb2.Revision
            details: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
            created_by: _actor_pb2.Actor
            idempotency_key: str
            def __init__(self, message: _Optional[str] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., details: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., created_by: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., idempotency_key: _Optional[str] = ...) -> None: ...
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        VERSION_FIELD_NUMBER: _ClassVar[int]
        LAST_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        STATE_HISTORY_FIELD_NUMBER: _ClassVar[int]
        WAITING_UNTIL_FIELD_NUMBER: _ClassVar[int]
        PROCESS_UID_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        PROGRESS_FIELD_NUMBER: _ClassVar[int]
        EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.StageAttempt
        version: _revision_pb2.Revision
        last_heartbeat: _revision_pb2.Revision
        state: _stage_attempt_state_pb2.StageAttemptState
        state_history: _containers.RepeatedCompositeFieldContainer[Stage.Attempt.StateHistoryEntry]
        waiting_until: _timestamp_pb2.Timestamp
        process_uid: str
        details: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
        progress: _containers.RepeatedCompositeFieldContainer[Stage.Attempt.Progress]
        execution_policy: _stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.StageAttempt, _Mapping]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., last_heartbeat: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., state: _Optional[_Union[_stage_attempt_state_pb2.StageAttemptState, str]] = ..., state_history: _Optional[_Iterable[_Union[Stage.Attempt.StateHistoryEntry, _Mapping]]] = ..., waiting_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., process_uid: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ..., progress: _Optional[_Iterable[_Union[Stage.Attempt.Progress, _Mapping]]] = ..., execution_policy: _Optional[_Union[_stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy, _Mapping]] = ...) -> None: ...
    class Assignment(_message.Message):
        __slots__ = ("target", "goal_state")
        TARGET_FIELD_NUMBER: _ClassVar[int]
        GOAL_STATE_FIELD_NUMBER: _ClassVar[int]
        target: _identifier_pb2.Check
        goal_state: _check_state_pb2.CheckState
        def __init__(self, target: _Optional[_Union[_identifier_pb2.Check, _Mapping]] = ..., goal_state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ...) -> None: ...
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_BY_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    LEGACY_FIELD_NUMBER: _ClassVar[int]
    STATE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    CONTINUATION_GROUP_FIELD_NUMBER: _ClassVar[int]
    CONCLUDED_REASON_FIELD_NUMBER: _ClassVar[int]
    EDITS_FIELD_NUMBER: _ClassVar[int]
    identifier: _identifier_pb2.Stage
    display_name: str
    created_by: _actor_pb2.Actor
    realm: str
    args: _value_ref_pb2.ValueRef
    sub_type: str
    version: _revision_pb2.Revision
    state: _stage_state_pb2.StageState
    cancelled_by: _actor_pb2.Actor
    cancelled_at: _revision_pb2.Revision
    legacy: Stage.Legacy
    state_history: _containers.RepeatedCompositeFieldContainer[Stage.StateHistoryEntry]
    dependencies: _dependencies_pb2.Dependencies
    execution_policy: Stage.ExecutionPolicyState
    attempts: _containers.RepeatedCompositeFieldContainer[Stage.Attempt]
    assignments: _containers.RepeatedCompositeFieldContainer[Stage.Assignment]
    continuation_group: _dependencies_pb2.Dependencies
    concluded_reason: _stage_concluded_reason_pb2.StageConcludedReason
    edits: _containers.RepeatedCompositeFieldContainer[_edit_pb2.Edit]
    def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Stage, _Mapping]] = ..., display_name: _Optional[str] = ..., created_by: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., realm: _Optional[str] = ..., args: _Optional[_Union[_value_ref_pb2.ValueRef, _Mapping]] = ..., sub_type: _Optional[str] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., cancelled_by: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., cancelled_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., legacy: _Optional[_Union[Stage.Legacy, _Mapping]] = ..., state_history: _Optional[_Iterable[_Union[Stage.StateHistoryEntry, _Mapping]]] = ..., dependencies: _Optional[_Union[_dependencies_pb2.Dependencies, _Mapping]] = ..., execution_policy: _Optional[_Union[Stage.ExecutionPolicyState, _Mapping]] = ..., attempts: _Optional[_Iterable[_Union[Stage.Attempt, _Mapping]]] = ..., assignments: _Optional[_Iterable[_Union[Stage.Assignment, _Mapping]]] = ..., continuation_group: _Optional[_Union[_dependencies_pb2.Dependencies, _Mapping]] = ..., concluded_reason: _Optional[_Union[_stage_concluded_reason_pb2.StageConcludedReason, str]] = ..., edits: _Optional[_Iterable[_Union[_edit_pb2.Edit, _Mapping]]] = ...) -> None: ...

class StageAttemptClaimedFailure(_message.Message):
    __slots__ = ("claimed_by_process_uid",)
    CLAIMED_BY_PROCESS_UID_FIELD_NUMBER: _ClassVar[int]
    claimed_by_process_uid: str
    def __init__(self, claimed_by_process_uid: _Optional[str] = ...) -> None: ...

class StageAttemptCurrentState(_message.Message):
    __slots__ = ("state", "version", "update_state_by", "heartbeat_by", "cancelled_at")
    STATE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPDATE_STATE_BY_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_BY_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    state: _stage_attempt_state_pb2.StageAttemptState
    version: _revision_pb2.Revision
    update_state_by: _timestamp_pb2.Timestamp
    heartbeat_by: _timestamp_pb2.Timestamp
    cancelled_at: _revision_pb2.Revision
    def __init__(self, state: _Optional[_Union[_stage_attempt_state_pb2.StageAttemptState, str]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., update_state_by: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., heartbeat_by: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., cancelled_at: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ...) -> None: ...
