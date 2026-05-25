from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.code_submission import CodeSubmissionStatus


class SubmitCodeSubmissionRequest(BaseModel):
    source_code: str = Field(min_length=1)


class CodeSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code_task_id: UUID
    student_id: UUID
    source_code: str
    attempt_number: int
    status: CodeSubmissionStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None