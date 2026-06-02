from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateWorkPlanRequest(_message.Message):
    __slots__ = ("realm", "idempotency_key", "workflow_name")
    REALM_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_NAME_FIELD_NUMBER: _ClassVar[int]
    realm: str
    idempotency_key: str
    workflow_name: str
    def __init__(self, realm: _Optional[str] = ..., idempotency_key: _Optional[str] = ..., workflow_name: _Optional[str] = ...) -> None: ...
