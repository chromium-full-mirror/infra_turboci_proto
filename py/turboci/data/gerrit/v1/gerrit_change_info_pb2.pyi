import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GerritChangeInfo(_message.Message):
    __slots__ = ("host", "project", "branch", "full_branch", "change_number", "patchset", "status", "creation_time", "last_modification_time", "submitted_time", "current_revision", "revisions", "owner", "reviewers", "labels", "messages", "change_id", "topic", "local", "is_owner_bot", "cherrypicked_from")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNKNOWN: _ClassVar[GerritChangeInfo.Status]
        STATUS_NEW: _ClassVar[GerritChangeInfo.Status]
        STATUS_MERGED: _ClassVar[GerritChangeInfo.Status]
        STATUS_ABANDONED: _ClassVar[GerritChangeInfo.Status]
        STATUS_MERGE_CONFLICT: _ClassVar[GerritChangeInfo.Status]
    STATUS_UNKNOWN: GerritChangeInfo.Status
    STATUS_NEW: GerritChangeInfo.Status
    STATUS_MERGED: GerritChangeInfo.Status
    STATUS_ABANDONED: GerritChangeInfo.Status
    STATUS_MERGE_CONFLICT: GerritChangeInfo.Status
    class RevisionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RevisionInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RevisionInfo, _Mapping]] = ...) -> None: ...
    class ReviewersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AccountInfos
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AccountInfos, _Mapping]] = ...) -> None: ...
    class LabelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: LabelInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[LabelInfo, _Mapping]] = ...) -> None: ...
    HOST_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    FULL_BRANCH_FIELD_NUMBER: _ClassVar[int]
    CHANGE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PATCHSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFICATION_TIME_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_TIME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_REVISION_FIELD_NUMBER: _ClassVar[int]
    REVISIONS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    REVIEWERS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    CHANGE_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FIELD_NUMBER: _ClassVar[int]
    IS_OWNER_BOT_FIELD_NUMBER: _ClassVar[int]
    CHERRYPICKED_FROM_FIELD_NUMBER: _ClassVar[int]
    host: str
    project: str
    branch: str
    full_branch: str
    change_number: int
    patchset: int
    status: GerritChangeInfo.Status
    creation_time: _timestamp_pb2.Timestamp
    last_modification_time: _timestamp_pb2.Timestamp
    submitted_time: _timestamp_pb2.Timestamp
    current_revision: str
    revisions: _containers.MessageMap[str, RevisionInfo]
    owner: AccountInfo
    reviewers: _containers.MessageMap[str, AccountInfos]
    labels: _containers.MessageMap[str, LabelInfo]
    messages: _containers.RepeatedCompositeFieldContainer[ChangeMessageInfo]
    change_id: str
    topic: str
    local: bool
    is_owner_bot: bool
    cherrypicked_from: str
    def __init__(self, host: _Optional[str] = ..., project: _Optional[str] = ..., branch: _Optional[str] = ..., full_branch: _Optional[str] = ..., change_number: _Optional[int] = ..., patchset: _Optional[int] = ..., status: _Optional[_Union[GerritChangeInfo.Status, str]] = ..., creation_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_modification_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., submitted_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., current_revision: _Optional[str] = ..., revisions: _Optional[_Mapping[str, RevisionInfo]] = ..., owner: _Optional[_Union[AccountInfo, _Mapping]] = ..., reviewers: _Optional[_Mapping[str, AccountInfos]] = ..., labels: _Optional[_Mapping[str, LabelInfo]] = ..., messages: _Optional[_Iterable[_Union[ChangeMessageInfo, _Mapping]]] = ..., change_id: _Optional[str] = ..., topic: _Optional[str] = ..., local: _Optional[bool] = ..., is_owner_bot: _Optional[bool] = ..., cherrypicked_from: _Optional[str] = ...) -> None: ...

class AccountInfo(_message.Message):
    __slots__ = ("account_id", "name", "display_name", "email", "secondary_emails", "username", "status", "inactive", "deleted", "tags")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_EMAILS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    name: str
    display_name: str
    email: str
    secondary_emails: _containers.RepeatedScalarFieldContainer[str]
    username: str
    status: str
    inactive: bool
    deleted: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, account_id: _Optional[int] = ..., name: _Optional[str] = ..., display_name: _Optional[str] = ..., email: _Optional[str] = ..., secondary_emails: _Optional[_Iterable[str]] = ..., username: _Optional[str] = ..., status: _Optional[str] = ..., inactive: _Optional[bool] = ..., deleted: _Optional[bool] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class AccountInfos(_message.Message):
    __slots__ = ("accounts",)
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[AccountInfo]
    def __init__(self, accounts: _Optional[_Iterable[_Union[AccountInfo, _Mapping]]] = ...) -> None: ...

class ApprovalInfo(_message.Message):
    __slots__ = ("user", "value", "date", "tag", "post_submit")
    USER_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    POST_SUBMIT_FIELD_NUMBER: _ClassVar[int]
    user: AccountInfo
    value: int
    date: _timestamp_pb2.Timestamp
    tag: str
    post_submit: bool
    def __init__(self, user: _Optional[_Union[AccountInfo, _Mapping]] = ..., value: _Optional[int] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., tag: _Optional[str] = ..., post_submit: _Optional[bool] = ...) -> None: ...

class ChangeMessageInfo(_message.Message):
    __slots__ = ("id", "author", "real_author", "date", "message", "accounts_in_message", "tag", "patchset")
    ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    REAL_AUTHOR_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNTS_IN_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    PATCHSET_FIELD_NUMBER: _ClassVar[int]
    id: str
    author: AccountInfo
    real_author: AccountInfo
    date: _timestamp_pb2.Timestamp
    message: str
    accounts_in_message: _containers.RepeatedCompositeFieldContainer[AccountInfo]
    tag: str
    patchset: int
    def __init__(self, id: _Optional[str] = ..., author: _Optional[_Union[AccountInfo, _Mapping]] = ..., real_author: _Optional[_Union[AccountInfo, _Mapping]] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[str] = ..., accounts_in_message: _Optional[_Iterable[_Union[AccountInfo, _Mapping]]] = ..., tag: _Optional[str] = ..., patchset: _Optional[int] = ...) -> None: ...

class CommitInfo(_message.Message):
    __slots__ = ("commit_id", "parents", "author", "committer", "subject", "message", "is_robot_commit", "bug_id", "tree_id", "date")
    COMMIT_ID_FIELD_NUMBER: _ClassVar[int]
    PARENTS_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    COMMITTER_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IS_ROBOT_COMMIT_FIELD_NUMBER: _ClassVar[int]
    BUG_ID_FIELD_NUMBER: _ClassVar[int]
    TREE_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    commit_id: str
    parents: _containers.RepeatedCompositeFieldContainer[CommitInfo]
    author: AccountInfo
    committer: AccountInfo
    subject: str
    message: str
    is_robot_commit: bool
    bug_id: _containers.RepeatedScalarFieldContainer[int]
    tree_id: str
    date: _timestamp_pb2.Timestamp
    def __init__(self, commit_id: _Optional[str] = ..., parents: _Optional[_Iterable[_Union[CommitInfo, _Mapping]]] = ..., author: _Optional[_Union[AccountInfo, _Mapping]] = ..., committer: _Optional[_Union[AccountInfo, _Mapping]] = ..., subject: _Optional[str] = ..., message: _Optional[str] = ..., is_robot_commit: _Optional[bool] = ..., bug_id: _Optional[_Iterable[int]] = ..., tree_id: _Optional[str] = ..., date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ("old_path", "status", "lines_inserted", "lines_deleted")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNKNOWN: _ClassVar[FileInfo.Status]
        STATUS_ADDED: _ClassVar[FileInfo.Status]
        STATUS_DELETED: _ClassVar[FileInfo.Status]
        STATUS_MODIFIED: _ClassVar[FileInfo.Status]
        STATUS_RENAMED: _ClassVar[FileInfo.Status]
        STATUS_COPIED: _ClassVar[FileInfo.Status]
        STATUS_REWRITTEN: _ClassVar[FileInfo.Status]
    STATUS_UNKNOWN: FileInfo.Status
    STATUS_ADDED: FileInfo.Status
    STATUS_DELETED: FileInfo.Status
    STATUS_MODIFIED: FileInfo.Status
    STATUS_RENAMED: FileInfo.Status
    STATUS_COPIED: FileInfo.Status
    STATUS_REWRITTEN: FileInfo.Status
    OLD_PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LINES_INSERTED_FIELD_NUMBER: _ClassVar[int]
    LINES_DELETED_FIELD_NUMBER: _ClassVar[int]
    old_path: str
    status: FileInfo.Status
    lines_inserted: int
    lines_deleted: int
    def __init__(self, old_path: _Optional[str] = ..., status: _Optional[_Union[FileInfo.Status, str]] = ..., lines_inserted: _Optional[int] = ..., lines_deleted: _Optional[int] = ...) -> None: ...

class LabelInfo(_message.Message):
    __slots__ = ("description", "value", "default_value", "all", "values")
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    description: str
    value: int
    default_value: int
    all: _containers.RepeatedCompositeFieldContainer[ApprovalInfo]
    values: _containers.ScalarMap[str, str]
    def __init__(self, description: _Optional[str] = ..., value: _Optional[int] = ..., default_value: _Optional[int] = ..., all: _Optional[_Iterable[_Union[ApprovalInfo, _Mapping]]] = ..., values: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RevisionInfo(_message.Message):
    __slots__ = ("kind", "patchset", "created", "uploader", "ref", "commit", "files")
    class Kind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        KIND_UNKNOWN: _ClassVar[RevisionInfo.Kind]
        KIND_REWORK: _ClassVar[RevisionInfo.Kind]
        KIND_TRIVIAL_REBASE: _ClassVar[RevisionInfo.Kind]
        KIND_TRIVIAL_REBASE_WITH_MESSAGE_UPDATE: _ClassVar[RevisionInfo.Kind]
        KIND_MERGE_FIRST_PARENT_UPDATE: _ClassVar[RevisionInfo.Kind]
        KIND_NO_CODE_CHANGE: _ClassVar[RevisionInfo.Kind]
        KIND_NO_CHANGE: _ClassVar[RevisionInfo.Kind]
    KIND_UNKNOWN: RevisionInfo.Kind
    KIND_REWORK: RevisionInfo.Kind
    KIND_TRIVIAL_REBASE: RevisionInfo.Kind
    KIND_TRIVIAL_REBASE_WITH_MESSAGE_UPDATE: RevisionInfo.Kind
    KIND_MERGE_FIRST_PARENT_UPDATE: RevisionInfo.Kind
    KIND_NO_CODE_CHANGE: RevisionInfo.Kind
    KIND_NO_CHANGE: RevisionInfo.Kind
    class FilesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FileInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FileInfo, _Mapping]] = ...) -> None: ...
    KIND_FIELD_NUMBER: _ClassVar[int]
    PATCHSET_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPLOADER_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    kind: RevisionInfo.Kind
    patchset: int
    created: _timestamp_pb2.Timestamp
    uploader: AccountInfo
    ref: str
    commit: CommitInfo
    files: _containers.MessageMap[str, FileInfo]
    def __init__(self, kind: _Optional[_Union[RevisionInfo.Kind, str]] = ..., patchset: _Optional[int] = ..., created: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., uploader: _Optional[_Union[AccountInfo, _Mapping]] = ..., ref: _Optional[str] = ..., commit: _Optional[_Union[CommitInfo, _Mapping]] = ..., files: _Optional[_Mapping[str, FileInfo]] = ...) -> None: ...
