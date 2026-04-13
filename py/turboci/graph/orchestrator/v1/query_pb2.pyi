from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import check_kind_pb2 as _check_kind_pb2
from turboci.graph.orchestrator.v1 import check_state_pb2 as _check_state_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_range_pb2 as _revision_range_pb2
from turboci.graph.orchestrator.v1 import stage_state_pb2 as _stage_state_pb2
from turboci.graph.orchestrator.v1 import type_set_pb2 as _type_set_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryExpandDepsMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUERY_EXPAND_DEPS_MODE_UNKNOWN: _ClassVar[QueryExpandDepsMode]
    QUERY_EXPAND_DEPS_MODE_EDGES: _ClassVar[QueryExpandDepsMode]
    QUERY_EXPAND_DEPS_MODE_SATISFIED: _ClassVar[QueryExpandDepsMode]

class CollectStageAttempts(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLLECT_STAGE_ATTEMPTS_UNKNOWN: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_NONE: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_ALL: _ClassVar[CollectStageAttempts]
    COLLECT_STAGE_ATTEMPTS_LATEST: _ClassVar[CollectStageAttempts]
QUERY_EXPAND_DEPS_MODE_UNKNOWN: QueryExpandDepsMode
QUERY_EXPAND_DEPS_MODE_EDGES: QueryExpandDepsMode
QUERY_EXPAND_DEPS_MODE_SATISFIED: QueryExpandDepsMode
COLLECT_STAGE_ATTEMPTS_UNKNOWN: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_NONE: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_ALL: CollectStageAttempts
COLLECT_STAGE_ATTEMPTS_LATEST: CollectStageAttempts

class Query(_message.Message):
    __slots__ = ("nodes_in_workplan", "nodes_across_workplans", "nodes_by_id", "select_checks", "select_stages", "expand_dependencies", "expand_dependents", "collect_checks", "collect_stages")
    class NodesAcrossWorkPlans(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class NodesByID(_message.Message):
        __slots__ = ("nodes",)
        NODES_FIELD_NUMBER: _ClassVar[int]
        nodes: _containers.RepeatedCompositeFieldContainer[_identifier_pb2.Identifier]
        def __init__(self, nodes: _Optional[_Iterable[_Union[_identifier_pb2.Identifier, _Mapping]]] = ...) -> None: ...
    class SelectChecks(_message.Message):
        __slots__ = ("predicates",)
        class Predicate(_message.Message):
            __slots__ = ("kind", "state", "with_option_type", "with_result_data_type")
            KIND_FIELD_NUMBER: _ClassVar[int]
            STATE_FIELD_NUMBER: _ClassVar[int]
            WITH_OPTION_TYPE_FIELD_NUMBER: _ClassVar[int]
            WITH_RESULT_DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
            kind: _check_kind_pb2.CheckKind
            state: _check_state_pb2.CheckState
            with_option_type: _type_set_pb2.TypeSet
            with_result_data_type: _type_set_pb2.TypeSet
            def __init__(self, kind: _Optional[_Union[_check_kind_pb2.CheckKind, str]] = ..., state: _Optional[_Union[_check_state_pb2.CheckState, str]] = ..., with_option_type: _Optional[_Union[_type_set_pb2.TypeSet, _Mapping]] = ..., with_result_data_type: _Optional[_Union[_type_set_pb2.TypeSet, _Mapping]] = ...) -> None: ...
        PREDICATES_FIELD_NUMBER: _ClassVar[int]
        predicates: _containers.RepeatedCompositeFieldContainer[Query.SelectChecks.Predicate]
        def __init__(self, predicates: _Optional[_Iterable[_Union[Query.SelectChecks.Predicate, _Mapping]]] = ...) -> None: ...
    class SelectStages(_message.Message):
        __slots__ = ("predicates",)
        class Predicate(_message.Message):
            __slots__ = ("state", "with_args_type")
            STATE_FIELD_NUMBER: _ClassVar[int]
            WITH_ARGS_TYPE_FIELD_NUMBER: _ClassVar[int]
            state: _stage_state_pb2.StageState
            with_args_type: _type_set_pb2.TypeSet
            def __init__(self, state: _Optional[_Union[_stage_state_pb2.StageState, str]] = ..., with_args_type: _Optional[_Union[_type_set_pb2.TypeSet, _Mapping]] = ...) -> None: ...
        PREDICATES_FIELD_NUMBER: _ClassVar[int]
        predicates: _containers.RepeatedCompositeFieldContainer[Query.SelectStages.Predicate]
        def __init__(self, predicates: _Optional[_Iterable[_Union[Query.SelectStages.Predicate, _Mapping]]] = ...) -> None: ...
    class ExpandDependencies(_message.Message):
        __slots__ = ("mode",)
        MODE_FIELD_NUMBER: _ClassVar[int]
        mode: QueryExpandDepsMode
        def __init__(self, mode: _Optional[_Union[QueryExpandDepsMode, str]] = ...) -> None: ...
    class ExpandDependents(_message.Message):
        __slots__ = ("mode",)
        MODE_FIELD_NUMBER: _ClassVar[int]
        mode: QueryExpandDepsMode
        def __init__(self, mode: _Optional[_Union[QueryExpandDepsMode, str]] = ...) -> None: ...
    class CollectChecks(_message.Message):
        __slots__ = ("options", "result_data", "edits")
        OPTIONS_FIELD_NUMBER: _ClassVar[int]
        RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
        EDITS_FIELD_NUMBER: _ClassVar[int]
        options: bool
        result_data: bool
        edits: _revision_range_pb2.RevisionRange
        def __init__(self, options: _Optional[bool] = ..., result_data: _Optional[bool] = ..., edits: _Optional[_Union[_revision_range_pb2.RevisionRange, _Mapping]] = ...) -> None: ...
    class CollectStages(_message.Message):
        __slots__ = ("attempts", "edits")
        ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
        EDITS_FIELD_NUMBER: _ClassVar[int]
        attempts: CollectStageAttempts
        edits: _revision_range_pb2.RevisionRange
        def __init__(self, attempts: _Optional[_Union[CollectStageAttempts, str]] = ..., edits: _Optional[_Union[_revision_range_pb2.RevisionRange, _Mapping]] = ...) -> None: ...
    NODES_IN_WORKPLAN_FIELD_NUMBER: _ClassVar[int]
    NODES_ACROSS_WORKPLANS_FIELD_NUMBER: _ClassVar[int]
    NODES_BY_ID_FIELD_NUMBER: _ClassVar[int]
    SELECT_CHECKS_FIELD_NUMBER: _ClassVar[int]
    SELECT_STAGES_FIELD_NUMBER: _ClassVar[int]
    EXPAND_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    EXPAND_DEPENDENTS_FIELD_NUMBER: _ClassVar[int]
    COLLECT_CHECKS_FIELD_NUMBER: _ClassVar[int]
    COLLECT_STAGES_FIELD_NUMBER: _ClassVar[int]
    nodes_in_workplan: _identifier_pb2.WorkPlan
    nodes_across_workplans: Query.NodesAcrossWorkPlans
    nodes_by_id: Query.NodesByID
    select_checks: Query.SelectChecks
    select_stages: Query.SelectStages
    expand_dependencies: Query.ExpandDependencies
    expand_dependents: Query.ExpandDependents
    collect_checks: Query.CollectChecks
    collect_stages: Query.CollectStages
    def __init__(self, nodes_in_workplan: _Optional[_Union[_identifier_pb2.WorkPlan, _Mapping]] = ..., nodes_across_workplans: _Optional[_Union[Query.NodesAcrossWorkPlans, _Mapping]] = ..., nodes_by_id: _Optional[_Union[Query.NodesByID, _Mapping]] = ..., select_checks: _Optional[_Union[Query.SelectChecks, _Mapping]] = ..., select_stages: _Optional[_Union[Query.SelectStages, _Mapping]] = ..., expand_dependencies: _Optional[_Union[Query.ExpandDependencies, _Mapping]] = ..., expand_dependents: _Optional[_Union[Query.ExpandDependents, _Mapping]] = ..., collect_checks: _Optional[_Union[Query.CollectChecks, _Mapping]] = ..., collect_stages: _Optional[_Union[Query.CollectStages, _Mapping]] = ...) -> None: ...
