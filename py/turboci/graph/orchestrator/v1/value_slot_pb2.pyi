from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ValueSlot(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_SLOT_UNKNOWN: _ClassVar[ValueSlot]
    VALUE_SLOT_CHECK_OPTION: _ClassVar[ValueSlot]
    VALUE_SLOT_CHECK_RESULT_DATA: _ClassVar[ValueSlot]
    VALUE_SLOT_CHECK_EDIT_REASON_DETAIL: _ClassVar[ValueSlot]
    VALUE_SLOT_CHECK_EDIT_OPTION: _ClassVar[ValueSlot]
    VALUE_SLOT_CHECK_EDIT_RESULT_DATA: _ClassVar[ValueSlot]
    VALUE_SLOT_STAGE_ARGS: _ClassVar[ValueSlot]
    VALUE_SLOT_STAGE_LEGACY_WORKNODE: _ClassVar[ValueSlot]
    VALUE_SLOT_ATTEMPT_DETAIL: _ClassVar[ValueSlot]
    VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL: _ClassVar[ValueSlot]
    VALUE_SLOT_STAGE_EDIT_REASON_DETAIL: _ClassVar[ValueSlot]
    VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL: _ClassVar[ValueSlot]
    VALUE_SLOT_ALL: _ClassVar[ValueSlot]
VALUE_SLOT_UNKNOWN: ValueSlot
VALUE_SLOT_CHECK_OPTION: ValueSlot
VALUE_SLOT_CHECK_RESULT_DATA: ValueSlot
VALUE_SLOT_CHECK_EDIT_REASON_DETAIL: ValueSlot
VALUE_SLOT_CHECK_EDIT_OPTION: ValueSlot
VALUE_SLOT_CHECK_EDIT_RESULT_DATA: ValueSlot
VALUE_SLOT_STAGE_ARGS: ValueSlot
VALUE_SLOT_STAGE_LEGACY_WORKNODE: ValueSlot
VALUE_SLOT_ATTEMPT_DETAIL: ValueSlot
VALUE_SLOT_ATTEMPT_PROGRESS_DETAIL: ValueSlot
VALUE_SLOT_STAGE_EDIT_REASON_DETAIL: ValueSlot
VALUE_SLOT_STAGE_EDIT_ATTEMPT_DETAIL: ValueSlot
VALUE_SLOT_ALL: ValueSlot
