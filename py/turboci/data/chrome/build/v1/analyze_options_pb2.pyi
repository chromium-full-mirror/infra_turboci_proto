from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzeOptions(_message.Message):
    __slots__ = ("compile_targets", "test_targets", "analyze_config_path", "analyze_config_names", "additional_exclusions")
    class AdditionalExclusionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COMPILE_TARGETS_FIELD_NUMBER: _ClassVar[int]
    TEST_TARGETS_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_CONFIG_PATH_FIELD_NUMBER: _ClassVar[int]
    ANALYZE_CONFIG_NAMES_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_EXCLUSIONS_FIELD_NUMBER: _ClassVar[int]
    compile_targets: _containers.RepeatedScalarFieldContainer[str]
    test_targets: _containers.RepeatedScalarFieldContainer[str]
    analyze_config_path: str
    analyze_config_names: _containers.RepeatedScalarFieldContainer[str]
    additional_exclusions: _containers.ScalarMap[str, str]
    def __init__(self, compile_targets: _Optional[_Iterable[str]] = ..., test_targets: _Optional[_Iterable[str]] = ..., analyze_config_path: _Optional[str] = ..., analyze_config_names: _Optional[_Iterable[str]] = ..., additional_exclusions: _Optional[_Mapping[str, str]] = ...) -> None: ...
