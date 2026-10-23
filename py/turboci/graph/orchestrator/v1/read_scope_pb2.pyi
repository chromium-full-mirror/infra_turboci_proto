from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ReadScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    READ_SCOPE_NODE: _ClassVar[ReadScope]
    READ_SCOPE_WORKPLAN: _ClassVar[ReadScope]
READ_SCOPE_NODE: ReadScope
READ_SCOPE_WORKPLAN: ReadScope
