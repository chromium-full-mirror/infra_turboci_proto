from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ValueMask(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALUE_MASK_UNKNOWN: _ClassVar[ValueMask]
    VALUE_MASK_TYPE: _ClassVar[ValueMask]
    VALUE_MASK_VALUE_TYPE: _ClassVar[ValueMask]
VALUE_MASK_UNKNOWN: ValueMask
VALUE_MASK_TYPE: ValueMask
VALUE_MASK_VALUE_TYPE: ValueMask
