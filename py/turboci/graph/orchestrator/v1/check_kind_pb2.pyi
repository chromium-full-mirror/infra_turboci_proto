from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CheckKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHECK_KIND_UNKNOWN: _ClassVar[CheckKind]
    CHECK_KIND_SOURCE: _ClassVar[CheckKind]
    CHECK_KIND_BUILD: _ClassVar[CheckKind]
    CHECK_KIND_TEST: _ClassVar[CheckKind]
    CHECK_KIND_ANALYSIS: _ClassVar[CheckKind]
CHECK_KIND_UNKNOWN: CheckKind
CHECK_KIND_SOURCE: CheckKind
CHECK_KIND_BUILD: CheckKind
CHECK_KIND_TEST: CheckKind
CHECK_KIND_ANALYSIS: CheckKind
