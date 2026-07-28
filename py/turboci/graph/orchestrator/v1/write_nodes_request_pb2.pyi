import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import check_kind_pb2 as _check_kind_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import edge_pb2 as _edge_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import stage_pb2 as _stage_pb2
from turboci.graph.orchestrator.v1 import stage_attempt_execution_policy_pb2 as _stage_attempt_execution_policy_pb2
from turboci.graph.orchestrator.v1 import stage_execution_policy_pb2 as _stage_execution_policy_pb2
from turboci.graph.orchestrator.v1 import transaction_details_pb2 as _transaction_details_pb2
from turboci.graph.orchestrator.v1 import value_write_pb2 as _value_write_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WriteNodesRequest(_message.Message):
    __slots__ = ("token", "reason", "txn", "checks", "stages", "current_attempt", "current_stage")
    class DependencyGroup(_message.Message):
        __slots__ = ("edges", "groups", "threshold")
        EDGES_FIELD_NUMBER: _ClassVar[int]
        GROUPS_FIELD_NUMBER: _ClassVar[int]
        THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        edges: _containers.RepeatedCompositeFieldContainer[_edge_pb2.Edge]
        groups: _containers.RepeatedCompositeFieldContainer[WriteNodesRequest.DependencyGroup]
        threshold: int
        def __init__(self, edges: _Optional[_Iterable[_Union[_edge_pb2.Edge, _Mapping]]] = ..., groups: _Optional[_Iterable[_Union[WriteNodesRequest.DependencyGroup, _Mapping]]] = ..., threshold: _Optional[int] = ...) -> None: ...
    class StageAttemptProgress(_message.Message):
        __slots__ = ("message", "details", "idempotency_key")
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
        message: str
        details: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        idempotency_key: str
        def __init__(self, message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ..., idempotency_key: _Optional[str] = ...) -> None: ...
    class Reason(_message.Message):
        __slots__ = ("message", "details")
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        message: str
        details: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        def __init__(self, message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ...) -> None: ...
    class CheckWrite(_message.Message):
        __slots__ = ("identifier", "realm", "kind", "sub_type", "display_name", "options", "dependencies", "result_data", "finalize_results", "state")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        REALM_FIELD_NUMBER: _ClassVar[int]
        KIND_FIELD_NUMBER: _ClassVar[int]
        SUB_TYPE_FIELD_NUMBER: _ClassVar[int]
        DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
        OPTIONS_FIELD_NUMBER: _ClassVar[int]
        DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
        FINALIZE_RESULTS_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.Check
        realm: str
        kind: _check_kind_pb2.CheckKind
        sub_type: str
        display_name: str
        options: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        dependencies: WriteNodesRequest.DependencyGroup
        result_data: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        finalize_results: bool
        state: _check_state_pb2.CheckState
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Check, _Mapping]] = ..., realm: _Optional[str] = ..., kind: _Optional[_Union[_check_kind_pb2.CheckKind, str]] = ..., sub_type: _Optional[str] = ..., display_name: _Optional[str] = ..., options: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ..., dependencies: _Optional[_Union[WriteNodesRequest.DependencyGroup, _Mapping]] = ..., result_data: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ..., finalize_results: _Optional[bool] = ..., state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ...) -> None: ...
    class StageWrite(_message.Message):
        __slots__ = ("identifier", "args", "realm", "display_name", "dependencies", "requested_stage_execution_policy", "assignments", "cancelled")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        ARGS_FIELD_NUMBER: _ClassVar[int]
        REALM_FIELD_NUMBER: _ClassVar[int]
        DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
        DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
        REQUESTED_STAGE_EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
        ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
        CANCELLED_FIELD_NUMBER: _ClassVar[int]
        identifier: _identifier_pb2.Stage
        args: _value_write_pb2.ValueWrite
        realm: str
        display_name: str
        dependencies: WriteNodesRequest.DependencyGroup
        requested_stage_execution_policy: _stage_execution_policy_pb2.StageExecutionPolicy
        assignments: _containers.RepeatedCompositeFieldContainer[_stage_pb2.Stage.Assignment]
        cancelled: bool
        def __init__(self, identifier: _Optional[_Union[_identifier_pb2.Stage, _Mapping]] = ..., args: _Optional[_Union[_value_write_pb2.ValueWrite, _Mapping]] = ..., realm: _Optional[str] = ..., display_name: _Optional[str] = ..., dependencies: _Optional[_Union[WriteNodesRequest.DependencyGroup, _Mapping]] = ..., requested_stage_execution_policy: _Optional[_Union[_stage_execution_policy_pb2.StageExecutionPolicy, _Mapping]] = ..., assignments: _Optional[_Iterable[_Union[_stage_pb2.Stage.Assignment, _Mapping]]] = ..., cancelled: _Optional[bool] = ...) -> None: ...
    class CurrentAttemptWrite(_message.Message):
        __slots__ = ("details", "progress", "state_transition")
        class StateTransition(_message.Message):
            __slots__ = ("throttled", "scheduled", "running", "tearing_down", "complete", "incomplete")
            class Throttled(_message.Message):
                __slots__ = ("until",)
                UNTIL_FIELD_NUMBER: _ClassVar[int]
                until: _timestamp_pb2.Timestamp
                def __init__(self, until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
            class Scheduled(_message.Message):
                __slots__ = ("attempt_execution_policy",)
                ATTEMPT_EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
                attempt_execution_policy: _stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy
                def __init__(self, attempt_execution_policy: _Optional[_Union[_stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy, _Mapping]] = ...) -> None: ...
            class Running(_message.Message):
                __slots__ = ("attempt_execution_policy", "process_uid")
                ATTEMPT_EXECUTION_POLICY_FIELD_NUMBER: _ClassVar[int]
                PROCESS_UID_FIELD_NUMBER: _ClassVar[int]
                attempt_execution_policy: _stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy
                process_uid: str
                def __init__(self, attempt_execution_policy: _Optional[_Union[_stage_attempt_execution_policy_pb2.StageAttemptExecutionPolicy, _Mapping]] = ..., process_uid: _Optional[str] = ...) -> None: ...
            class TearingDown(_message.Message):
                __slots__ = ()
                def __init__(self) -> None: ...
            class Complete(_message.Message):
                __slots__ = ()
                def __init__(self) -> None: ...
            class Incomplete(_message.Message):
                __slots__ = ("block_new_attempts", "throttle_next_attempt_until")
                BLOCK_NEW_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
                THROTTLE_NEXT_ATTEMPT_UNTIL_FIELD_NUMBER: _ClassVar[int]
                block_new_attempts: bool
                throttle_next_attempt_until: _timestamp_pb2.Timestamp
                def __init__(self, block_new_attempts: _Optional[bool] = ..., throttle_next_attempt_until: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
            THROTTLED_FIELD_NUMBER: _ClassVar[int]
            SCHEDULED_FIELD_NUMBER: _ClassVar[int]
            RUNNING_FIELD_NUMBER: _ClassVar[int]
            TEARING_DOWN_FIELD_NUMBER: _ClassVar[int]
            COMPLETE_FIELD_NUMBER: _ClassVar[int]
            INCOMPLETE_FIELD_NUMBER: _ClassVar[int]
            throttled: WriteNodesRequest.CurrentAttemptWrite.StateTransition.Throttled
            scheduled: WriteNodesRequest.CurrentAttemptWrite.StateTransition.Scheduled
            running: WriteNodesRequest.CurrentAttemptWrite.StateTransition.Running
            tearing_down: WriteNodesRequest.CurrentAttemptWrite.StateTransition.TearingDown
            complete: WriteNodesRequest.CurrentAttemptWrite.StateTransition.Complete
            incomplete: WriteNodesRequest.CurrentAttemptWrite.StateTransition.Incomplete
            def __init__(self, throttled: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.Throttled, _Mapping]] = ..., scheduled: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.Scheduled, _Mapping]] = ..., running: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.Running, _Mapping]] = ..., tearing_down: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.TearingDown, _Mapping]] = ..., complete: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.Complete, _Mapping]] = ..., incomplete: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition.Incomplete, _Mapping]] = ...) -> None: ...
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        PROGRESS_FIELD_NUMBER: _ClassVar[int]
        STATE_TRANSITION_FIELD_NUMBER: _ClassVar[int]
        details: _containers.RepeatedCompositeFieldContainer[_value_write_pb2.ValueWrite]
        progress: _containers.RepeatedCompositeFieldContainer[WriteNodesRequest.StageAttemptProgress]
        state_transition: WriteNodesRequest.CurrentAttemptWrite.StateTransition
        def __init__(self, details: _Optional[_Iterable[_Union[_value_write_pb2.ValueWrite, _Mapping]]] = ..., progress: _Optional[_Iterable[_Union[WriteNodesRequest.StageAttemptProgress, _Mapping]]] = ..., state_transition: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite.StateTransition, _Mapping]] = ...) -> None: ...
    class CurrentStageWrite(_message.Message):
        __slots__ = ("continuation_group",)
        CONTINUATION_GROUP_FIELD_NUMBER: _ClassVar[int]
        continuation_group: WriteNodesRequest.DependencyGroup
        def __init__(self, continuation_group: _Optional[_Union[WriteNodesRequest.DependencyGroup, _Mapping]] = ...) -> None: ...
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TXN_FIELD_NUMBER: _ClassVar[int]
    CHECKS_FIELD_NUMBER: _ClassVar[int]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STAGE_FIELD_NUMBER: _ClassVar[int]
    token: str
    reason: WriteNodesRequest.Reason
    txn: _transaction_details_pb2.TransactionDetails
    checks: _containers.RepeatedCompositeFieldContainer[WriteNodesRequest.CheckWrite]
    stages: _containers.RepeatedCompositeFieldContainer[WriteNodesRequest.StageWrite]
    current_attempt: WriteNodesRequest.CurrentAttemptWrite
    current_stage: WriteNodesRequest.CurrentStageWrite
    def __init__(self, token: _Optional[str] = ..., reason: _Optional[_Union[WriteNodesRequest.Reason, _Mapping]] = ..., txn: _Optional[_Union[_transaction_details_pb2.TransactionDetails, _Mapping]] = ..., checks: _Optional[_Iterable[_Union[WriteNodesRequest.CheckWrite, _Mapping]]] = ..., stages: _Optional[_Iterable[_Union[WriteNodesRequest.StageWrite, _Mapping]]] = ..., current_attempt: _Optional[_Union[WriteNodesRequest.CurrentAttemptWrite, _Mapping]] = ..., current_stage: _Optional[_Union[WriteNodesRequest.CurrentStageWrite, _Mapping]] = ...) -> None: ...
