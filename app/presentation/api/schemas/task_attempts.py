from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.task_attempt import TaskAttemptStatus


class SubmitTaskAnswerRequest(BaseModel):
    submitted_answer: str = Field(min_length=1)


class TaskAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    student_id: UUID
    submitted_answer: str
    attempt_number: int
    status: TaskAttemptStatus
    awarded_points: int | None
    checked_at: datetime | None
    created_at: datetime