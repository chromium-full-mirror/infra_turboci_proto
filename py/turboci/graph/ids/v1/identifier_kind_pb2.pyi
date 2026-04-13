from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class IdentifierKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDENTIFIER_KIND_UNKNOWN: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_WORK_PLAN: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_CHECK: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_CHECK_RESULT: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_CHECK_EDIT: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_STAGE: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_STAGE_ATTEMPT: _ClassVar[IdentifierKind]
    IDENTIFIER_KIND_STAGE_EDIT: _ClassVar[IdentifierKind]
IDENTIFIER_KIND_UNKNOWN: IdentifierKind
IDENTIFIER_KIND_WORK_PLAN: IdentifierKind
IDENTIFIER_KIND_CHECK: IdentifierKind
IDENTIFIER_KIND_CHECK_RESULT: IdentifierKind
IDENTIFIER_KIND_CHECK_EDIT: IdentifierKind
IDENTIFIER_KIND_STAGE: IdentifierKind
IDENTIFIER_KIND_STAGE_ATTEMPT: IdentifierKind
IDENTIFIER_KIND_STAGE_EDIT: IdentifierKind
