from turboci.data.common.v1 import display_message_pb2 as _display_message_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestCheckDescriptionOption(_message.Message):
    __slots__ = ("title", "display_message")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    title: str
    display_message: _display_message_pb2.DisplayMessage
    def __init__(self, title: _Optional[str] = ..., display_message: _Optional[_Union[_display_message_pb2.DisplayMessage, _Mapping]] = ...) -> None: ...
