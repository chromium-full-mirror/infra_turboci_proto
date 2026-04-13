from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class OmitReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OMIT_REASON_UNKNOWN: _ClassVar[OmitReason]
    OMIT_REASON_UNWANTED: _ClassVar[OmitReason]
    OMIT_REASON_NO_ACCESS: _ClassVar[OmitReason]
    OMIT_REASON_MISSING: _ClassVar[OmitReason]
OMIT_REASON_UNKNOWN: OmitReason
OMIT_REASON_UNWANTED: OmitReason
OMIT_REASON_NO_ACCESS: OmitReason
OMIT_REASON_MISSING: OmitReason
