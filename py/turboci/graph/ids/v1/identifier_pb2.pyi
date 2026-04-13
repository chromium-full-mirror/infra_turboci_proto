import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Identifier(_message.Message):
    __slots__ = ("work_plan", "check", "check_result", "check_edit", "stage", "stage_attempt", "stage_edit")
    WORK_PLAN_FIELD_NUMBER: _ClassVar[int]
    CHECK_FIELD_NUMBER: _ClassVar[int]
    CHECK_RESULT_FIELD_NUMBER: _ClassVar[int]
    CHECK_EDIT_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    STAGE_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    STAGE_EDIT_FIELD_NUMBER: _ClassVar[int]
    work_plan: WorkPlan
    check: Check
    check_result: CheckResult
    check_edit: CheckEdit
    stage: Stage
    stage_attempt: StageAttempt
    stage_edit: StageEdit
    def __init__(self, work_plan: _Optional[_Union[WorkPlan, _Mapping]] = ..., check: _Optional[_Union[Check, _Mapping]] = ..., check_result: _Optional[_Union[CheckResult, _Mapping]] = ..., check_edit: _Optional[_Union[CheckEdit, _Mapping]] = ..., stage: _Optional[_Union[Stage, _Mapping]] = ..., stage_attempt: _Optional[_Union[StageAttempt, _Mapping]] = ..., stage_edit: _Optional[_Union[StageEdit, _Mapping]] = ...) -> None: ...

class WorkPlan(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Check(_message.Message):
    __slots__ = ("work_plan", "id")
    WORK_PLAN_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    work_plan: WorkPlan
    id: str
    def __init__(self, work_plan: _Optional[_Union[WorkPlan, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class CheckResult(_message.Message):
    __slots__ = ("check", "idx")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    IDX_FIELD_NUMBER: _ClassVar[int]
    check: Check
    idx: int
    def __init__(self, check: _Optional[_Union[Check, _Mapping]] = ..., idx: _Optional[int] = ...) -> None: ...

class CheckEdit(_message.Message):
    __slots__ = ("check", "version")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    check: Check
    version: _timestamp_pb2.Timestamp
    def __init__(self, check: _Optional[_Union[Check, _Mapping]] = ..., version: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Stage(_message.Message):
    __slots__ = ("work_plan", "is_worknode", "id")
    WORK_PLAN_FIELD_NUMBER: _ClassVar[int]
    IS_WORKNODE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    work_plan: WorkPlan
    is_worknode: bool
    id: str
    def __init__(self, work_plan: _Optional[_Union[WorkPlan, _Mapping]] = ..., is_worknode: _Optional[bool] = ..., id: _Optional[str] = ...) -> None: ...

class StageAttempt(_message.Message):
    __slots__ = ("stage", "idx")
    STAGE_FIELD_NUMBER: _ClassVar[int]
    IDX_FIELD_NUMBER: _ClassVar[int]
    stage: Stage
    idx: int
    def __init__(self, stage: _Optional[_Union[Stage, _Mapping]] = ..., idx: _Optional[int] = ...) -> None: ...

class StageEdit(_message.Message):
    __slots__ = ("stage", "version")
    STAGE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    stage: Stage
    version: _timestamp_pb2.Timestamp
    def __init__(self, stage: _Optional[_Union[Stage, _Mapping]] = ..., version: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
