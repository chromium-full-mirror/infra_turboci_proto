from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GobSourceCheckOptions(_message.Message):
    __slots__ = ("gerrit_changes", "base_pinned_repos")
    class GerritChange(_message.Message):
        __slots__ = ("hostname", "change_number", "patchset", "mounts_to_apply")
        HOSTNAME_FIELD_NUMBER: _ClassVar[int]
        CHANGE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        PATCHSET_FIELD_NUMBER: _ClassVar[int]
        MOUNTS_TO_APPLY_FIELD_NUMBER: _ClassVar[int]
        hostname: str
        change_number: int
        patchset: int
        mounts_to_apply: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, hostname: _Optional[str] = ..., change_number: _Optional[int] = ..., patchset: _Optional[int] = ..., mounts_to_apply: _Optional[_Iterable[str]] = ...) -> None: ...
    class PinnedRepoMounts(_message.Message):
        __slots__ = ("project_commit", "manifest_commit", "mount_overrides")
        class GitCommit(_message.Message):
            __slots__ = ("host", "project", "id", "ref")
            HOST_FIELD_NUMBER: _ClassVar[int]
            PROJECT_FIELD_NUMBER: _ClassVar[int]
            ID_FIELD_NUMBER: _ClassVar[int]
            REF_FIELD_NUMBER: _ClassVar[int]
            host: str
            project: str
            id: str
            ref: str
            def __init__(self, host: _Optional[str] = ..., project: _Optional[str] = ..., id: _Optional[str] = ..., ref: _Optional[str] = ...) -> None: ...
        class ManifestCommit(_message.Message):
            __slots__ = ("commit", "path")
            COMMIT_FIELD_NUMBER: _ClassVar[int]
            PATH_FIELD_NUMBER: _ClassVar[int]
            commit: GobSourceCheckOptions.PinnedRepoMounts.GitCommit
            path: str
            def __init__(self, commit: _Optional[_Union[GobSourceCheckOptions.PinnedRepoMounts.GitCommit, _Mapping]] = ..., path: _Optional[str] = ...) -> None: ...
        class MountOverride(_message.Message):
            __slots__ = ("override", "mount")
            OVERRIDE_FIELD_NUMBER: _ClassVar[int]
            MOUNT_FIELD_NUMBER: _ClassVar[int]
            override: GobSourceCheckOptions.PinnedRepoMounts.GitCommit
            mount: str
            def __init__(self, override: _Optional[_Union[GobSourceCheckOptions.PinnedRepoMounts.GitCommit, _Mapping]] = ..., mount: _Optional[str] = ...) -> None: ...
        PROJECT_COMMIT_FIELD_NUMBER: _ClassVar[int]
        MANIFEST_COMMIT_FIELD_NUMBER: _ClassVar[int]
        MOUNT_OVERRIDES_FIELD_NUMBER: _ClassVar[int]
        project_commit: GobSourceCheckOptions.PinnedRepoMounts.GitCommit
        manifest_commit: GobSourceCheckOptions.PinnedRepoMounts.ManifestCommit
        mount_overrides: _containers.RepeatedCompositeFieldContainer[GobSourceCheckOptions.PinnedRepoMounts.MountOverride]
        def __init__(self, project_commit: _Optional[_Union[GobSourceCheckOptions.PinnedRepoMounts.GitCommit, _Mapping]] = ..., manifest_commit: _Optional[_Union[GobSourceCheckOptions.PinnedRepoMounts.ManifestCommit, _Mapping]] = ..., mount_overrides: _Optional[_Iterable[_Union[GobSourceCheckOptions.PinnedRepoMounts.MountOverride, _Mapping]]] = ...) -> None: ...
    GERRIT_CHANGES_FIELD_NUMBER: _ClassVar[int]
    BASE_PINNED_REPOS_FIELD_NUMBER: _ClassVar[int]
    gerrit_changes: _containers.RepeatedCompositeFieldContainer[GobSourceCheckOptions.GerritChange]
    base_pinned_repos: GobSourceCheckOptions.PinnedRepoMounts
    def __init__(self, gerrit_changes: _Optional[_Iterable[_Union[GobSourceCheckOptions.GerritChange, _Mapping]]] = ..., base_pinned_repos: _Optional[_Union[GobSourceCheckOptions.PinnedRepoMounts, _Mapping]] = ...) -> None: ...
