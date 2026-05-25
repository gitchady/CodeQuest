from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.code_task import CodeTaskLanguage


class CodeTaskWriteRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    statement: str = Field(min_length=1)
    position: int = Field(ge=1)
    language: CodeTaskLanguage
    starter_code: str = ''
    max_attempts: int = Field(ge=1)
    reward_points: int = Field(ge=1)
    time_limit_seconds: int = Field(ge=1)
    memory_limit_mb: int = Field(ge=16)


class CreateCodeTaskRequest(CodeTaskWriteRequest):
    pass


class UpdateCodeTaskRequest(CodeTaskWriteRequest):
    pass


class CodeTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    language: CodeTaskLanguage
    starter_code: str
    max_attempts: int
    reward_points: int
    time_limit_seconds: int
    memory_limit_mb: int