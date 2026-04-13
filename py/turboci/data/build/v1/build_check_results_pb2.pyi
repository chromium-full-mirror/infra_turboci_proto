from turboci.data.common.v1 import display_message_pb2 as _display_message_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BuildCheckResult(_message.Message):
    __slots__ = ("success", "display_message", "android_build_artifacts", "cas_manifest", "gcs_artifacts", "view_url")
    class AndroidBuildArtifacts(_message.Message):
        __slots__ = ("build_id", "target", "build_attempt")
        BUILD_ID_FIELD_NUMBER: _ClassVar[int]
        TARGET_FIELD_NUMBER: _ClassVar[int]
        BUILD_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
        build_id: str
        target: str
        build_attempt: str
        def __init__(self, build_id: _Optional[str] = ..., target: _Optional[str] = ..., build_attempt: _Optional[str] = ...) -> None: ...
    class CasManifest(_message.Message):
        __slots__ = ("manifest", "cas_instance", "cas_service", "client_version")
        class ManifestEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        MANIFEST_FIELD_NUMBER: _ClassVar[int]
        CAS_INSTANCE_FIELD_NUMBER: _ClassVar[int]
        CAS_SERVICE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
        manifest: _containers.ScalarMap[str, str]
        cas_instance: str
        cas_service: str
        client_version: str
        def __init__(self, manifest: _Optional[_Mapping[str, str]] = ..., cas_instance: _Optional[str] = ..., cas_service: _Optional[str] = ..., client_version: _Optional[str] = ...) -> None: ...
    class GcsArtifacts(_message.Message):
        __slots__ = ("root_directory_uri", "files_by_category")
        class Files(_message.Message):
            __slots__ = ("files",)
            FILES_FIELD_NUMBER: _ClassVar[int]
            files: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, files: _Optional[_Iterable[str]] = ...) -> None: ...
        class FilesByCategoryEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: BuildCheckResult.GcsArtifacts.Files
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BuildCheckResult.GcsArtifacts.Files, _Mapping]] = ...) -> None: ...
        ROOT_DIRECTORY_URI_FIELD_NUMBER: _ClassVar[int]
        FILES_BY_CATEGORY_FIELD_NUMBER: _ClassVar[int]
        root_directory_uri: str
        files_by_category: _containers.MessageMap[str, BuildCheckResult.GcsArtifacts.Files]
        def __init__(self, root_directory_uri: _Optional[str] = ..., files_by_category: _Optional[_Mapping[str, BuildCheckResult.GcsArtifacts.Files]] = ...) -> None: ...
    class GcsArtifactsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: BuildCheckResult.GcsArtifacts
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BuildCheckResult.GcsArtifacts, _Mapping]] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ANDROID_BUILD_ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    CAS_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    GCS_ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    VIEW_URL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    display_message: _display_message_pb2.DisplayMessage
    android_build_artifacts: BuildCheckResult.AndroidBuildArtifacts
    cas_manifest: BuildCheckResult.CasManifest
    gcs_artifacts: _containers.MessageMap[str, BuildCheckResult.GcsArtifacts]
    view_url: str
    def __init__(self, success: _Optional[bool] = ..., display_message: _Optional[_Union[_display_message_pb2.DisplayMessage, _Mapping]] = ..., android_build_artifacts: _Optional[_Union[BuildCheckResult.AndroidBuildArtifacts, _Mapping]] = ..., cas_manifest: _Optional[_Union[BuildCheckResult.CasManifest, _Mapping]] = ..., gcs_artifacts: _Optional[_Mapping[str, BuildCheckResult.GcsArtifacts]] = ..., view_url: _Optional[str] = ...) -> None: ...
