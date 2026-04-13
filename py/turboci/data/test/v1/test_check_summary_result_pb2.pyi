from turboci.data.common.v1 import display_message_pb2 as _display_message_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestCheckSummaryResult(_message.Message):
    __slots__ = ("success", "display_message", "test_count", "success_count", "failure_count", "skip_count", "view_url")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TEST_COUNT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_COUNT_FIELD_NUMBER: _ClassVar[int]
    SKIP_COUNT_FIELD_NUMBER: _ClassVar[int]
    VIEW_URL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    display_message: _display_message_pb2.DisplayMessage
    test_count: int
    success_count: int
    failure_count: int
    skip_count: int
    view_url: str
    def __init__(self, success: _Optional[bool] = ..., display_message: _Optional[_Union[_display_message_pb2.DisplayMessage, _Mapping]] = ..., test_count: _Optional[int] = ..., success_count: _Optional[int] = ..., failure_count: _Optional[int] = ..., skip_count: _Optional[int] = ..., view_url: _Optional[str] = ...) -> None: ...
