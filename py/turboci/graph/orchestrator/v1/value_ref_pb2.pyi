from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import any_pb2 as _any_pb2
from turboci.graph.orchestrator.v1 import omit_reason_pb2 as _omit_reason_pb2
from turboci.graph.orchestrator.v1 import tags_pb2 as _tags_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValueRef(_message.Message):
    __slots__ = ("type_url", "realm", "digest", "inline", "omit_reason", "tags")
    TYPE_URL_FIELD_NUMBER: _ClassVar[int]
    REALM_FIELD_NUMBER: _ClassVar[int]
    DIGEST_FIELD_NUMBER: _ClassVar[int]
    INLINE_FIELD_NUMBER: _ClassVar[int]
    OMIT_REASON_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    type_url: str
    realm: str
    digest: str
    inline: _any_pb2.Any
    omit_reason: _omit_reason_pb2.OmitReason
    tags: _containers.RepeatedCompositeFieldContainer[_tags_pb2.Tag]
    def __init__(self, type_url: _Optional[str] = ..., realm: _Optional[str] = ..., digest: _Optional[str] = ..., inline: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., omit_reason: _Optional[_Union[_omit_reason_pb2.OmitReason, str]] = ..., tags: _Optional[_Iterable[_Union[_tags_pb2.Tag, _Mapping]]] = ...) -> None: ...
