from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.task import TaskCheckType


class TaskWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    statement: str = Field(min_length=1)
    position: int = Field(ge=1)
    check_type: TaskCheckType
    expected_answer: str = ''
    accepted_answers: list[str] = Field(default_factory=list)
    answer_pattern: str = ''
    max_attempts: int = Field(ge=1)
    reward_points: int = Field(ge=1)


class CreateTaskRequest(TaskWriteRequest):
    pass


class UpdateTaskRequest(TaskWriteRequest):
    pass


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    check_type: TaskCheckType
    expected_answer: str
    accepted_answers: list[str]
    answer_pattern: str
    max_attempts: int
    reward_points: int