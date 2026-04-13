import datetime

from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from turboci.graph.ids.v1 import identifier_pb2 as _identifier_pb2
from turboci.graph.orchestrator.v1 import actor_pb2 as _actor_pb2
from turboci.graph.orchestrator.v1 import check_delta_pb2 as _check_delta_pb2
from turboci.graph.orchestrator.v1 import field_options_pb2 as _field_options_pb2
from turboci.graph.orchestrator.v1 import revision_pb2 as _revision_pb2
from turboci.graph.orchestrator.v1 import stage_delta_pb2 as _stage_delta_pb2
from turboci.graph.orchestrator.v1 import transaction_details_pb2 as _transaction_details_pb2
from turboci.graph.orchestrator.v1 import value_ref_pb2 as _value_ref_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Edit(_message.Message):
    __slots__ = ("for_node", "version", "expire_at", "realm", "created_by", "txn", "write_node_set", "reason", "check", "stage")
    class Reason(_message.Message):
        __slots__ = ("message", "details")
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        DETAILS_FIELD_NUMBER: _ClassVar[int]
        message: str
        details: _containers.RepeatedCompositeFieldContainer[_value_ref_pb2.ValueRef]
        def __init__(self, message: _Optional[str] = ..., details: _Optional[_Iterable[_Union[_value_ref_pb2.ValueRef, _Mapping]]] = ...) -> None: ...
    FOR_NODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_AT_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    TXN_FIELD_NUMBER: _ClassVar[int]
    WRITE_NODE_SET_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CHECK_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    for_node: _identifier_pb2.Identifier
    version: _revision_pb2.Revision
    expire_at: _timestamp_pb2.Timestamp
    realm: str
    created_by: _actor_pb2.Actor
    txn: _transaction_details_pb2.TransactionDetails
    write_node_set: _containers.RepeatedCompositeFieldContainer[_identifier_pb2.Identifier]
    reason: Edit.Reason
    check: _check_delta_pb2.CheckDelta
    stage: _stage_delta_pb2.StageDelta
    def __init__(self, for_node: _Optional[_Union[_identifier_pb2.Identifier, _Mapping]] = ..., version: _Optional[_Union[_revision_pb2.Revision, _Mapping]] = ..., expire_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., realm: _Optional[str] = ..., created_by: _Optional[_Union[_actor_pb2.Actor, _Mapping]] = ..., txn: _Optional[_Union[_transaction_details_pb2.TransactionDetails, _Mapping]] = ..., write_node_set: _Optional[_Iterable[_Union[_identifier_pb2.Identifier, _Mapping]]] = ..., reason: _Optional[_Union[Edit.Reason, _Mapping]] = ..., check: _Optional[_Union[_check_delta_pb2.CheckDelta, _Mapping]] = ..., stage: _Optional[_Union[_stage_delta_pb2.StageDelta, _Mapping]] = ...) -> None: ...
