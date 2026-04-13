from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Product(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCT_UNKNOWN: _ClassVar[Product]
    PRODUCT_ANDROID: _ClassVar[Product]
    PRODUCT_BROWSER: _ClassVar[Product]
    PRODUCT_CHROMEOS: _ClassVar[Product]
PRODUCT_UNKNOWN: Product
PRODUCT_ANDROID: Product
PRODUCT_BROWSER: Product
PRODUCT_CHROMEOS: Product

class BuildCheckOptions(_message.Message):
    __slots__ = ("target",)
    class BuildTarget(_message.Message):
        __slots__ = ("name", "namespace", "product", "platform", "device")
        NAME_FIELD_NUMBER: _ClassVar[int]
        NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        PRODUCT_FIELD_NUMBER: _ClassVar[int]
        PLATFORM_FIELD_NUMBER: _ClassVar[int]
        DEVICE_FIELD_NUMBER: _ClassVar[int]
        name: str
        namespace: str
        product: Product
        platform: str
        device: str
        def __init__(self, name: _Optional[str] = ..., namespace: _Optional[str] = ..., product: _Optional[_Union[Product, str]] = ..., platform: _Optional[str] = ..., device: _Optional[str] = ...) -> None: ...
    TARGET_FIELD_NUMBER: _ClassVar[int]
    target: BuildCheckOptions.BuildTarget
    def __init__(self, target: _Optional[_Union[BuildCheckOptions.BuildTarget, _Mapping]] = ...) -> None: ...
