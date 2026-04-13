from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommonStageAttemptDetails(_message.Message):
    __slots__ = ("view_urls",)
    class ViewUrlsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CommonStageAttemptDetails.UrlDetails
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CommonStageAttemptDetails.UrlDetails, _Mapping]] = ...) -> None: ...
    class UrlDetails(_message.Message):
        __slots__ = ("url",)
        URL_FIELD_NUMBER: _ClassVar[int]
        url: str
        def __init__(self, url: _Optional[str] = ...) -> None: ...
    VIEW_URLS_FIELD_NUMBER: _ClassVar[int]
    view_urls: _containers.MessageMap[str, CommonStageAttemptDetails.UrlDetails]
    def __init__(self, view_urls: _Optional[_Mapping[str, CommonStageAttemptDetails.UrlDetails]] = ...) -> None: ...
