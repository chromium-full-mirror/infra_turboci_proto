from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BotUpdateResults(_message.Message):
    __slots__ = ("manifest",)
    class GitCommit(_message.Message):
        __slots__ = ("host", "project", "id")
        HOST_FIELD_NUMBER: _ClassVar[int]
        PROJECT_FIELD_NUMBER: _ClassVar[int]
        ID_FIELD_NUMBER: _ClassVar[int]
        host: str
        project: str
        id: str
        def __init__(self, host: _Optional[str] = ..., project: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...
    class ManifestEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: BotUpdateResults.GitCommit
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BotUpdateResults.GitCommit, _Mapping]] = ...) -> None: ...
    MANIFEST_FIELD_NUMBER: _ClassVar[int]
    manifest: _containers.MessageMap[str, BotUpdateResults.GitCommit]
    def __init__(self, manifest: _Optional[_Mapping[str, BotUpdateResults.GitCommit]] = ...) -> None: ...
