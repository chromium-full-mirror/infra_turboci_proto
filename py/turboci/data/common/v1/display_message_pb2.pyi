from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DisplayMessage(_message.Message):
    __slots__ = ("message", "message_format")
    class MessageFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MESSAGE_FORMAT_UNKNOWN: _ClassVar[DisplayMessage.MessageFormat]
        MESSAGE_FORMAT_PLAIN_TEXT: _ClassVar[DisplayMessage.MessageFormat]
        MESSAGE_FORMAT_HTML: _ClassVar[DisplayMessage.MessageFormat]
        MESSAGE_FORMAT_MARKDOWN: _ClassVar[DisplayMessage.MessageFormat]
        MESSAGE_FORMAT_ANSI: _ClassVar[DisplayMessage.MessageFormat]
    MESSAGE_FORMAT_UNKNOWN: DisplayMessage.MessageFormat
    MESSAGE_FORMAT_PLAIN_TEXT: DisplayMessage.MessageFormat
    MESSAGE_FORMAT_HTML: DisplayMessage.MessageFormat
    MESSAGE_FORMAT_MARKDOWN: DisplayMessage.MessageFormat
    MESSAGE_FORMAT_ANSI: DisplayMessage.MessageFormat
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    message: str
    message_format: DisplayMessage.MessageFormat
    def __init__(self, message: _Optional[str] = ..., message_format: _Optional[_Union[DisplayMessage.MessageFormat, str]] = ...) -> None: ...
