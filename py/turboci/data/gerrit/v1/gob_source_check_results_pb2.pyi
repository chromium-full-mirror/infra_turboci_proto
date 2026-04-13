from turboci.data.gerrit.v1 import gerrit_change_info_pb2 as _gerrit_change_info_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GobSourceCheckResults(_message.Message):
    __slots__ = ("changes",)
    CHANGES_FIELD_NUMBER: _ClassVar[int]
    changes: _containers.RepeatedCompositeFieldContainer[_gerrit_change_info_pb2.GerritChangeInfo]
    def __init__(self, changes: _Optional[_Iterable[_Union[_gerrit_change_info_pb2.GerritChangeInfo, _Mapping]]] = ...) -> None: ...
