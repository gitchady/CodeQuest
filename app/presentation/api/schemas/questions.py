from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.question import QuestionType


class QuestionWriteRequest(BaseModel):
    text: str = Field(min_length=1)
    position: int = Field(ge=1)
    question_type: QuestionType
    max_attempts: int = Field(ge=1)
    reward_points: int = Field(ge=1)


class CreateQuestionRequest(QuestionWriteRequest):
    pass


class UpdateQuestionRequest(QuestionWriteRequest):
    pass


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int
    answer_option_ids: list[UUID]


class AnswerOptionWriteRequest(BaseModel):
    text: str = Field(min_length=1)
    position: int = Field(ge=1)
    is_correct: bool = False


class CreateAnswerOptionRequest(AnswerOptionWriteRequest):
    pass


class UpdateAnswerOptionRequest(AnswerOptionWriteRequest):
    pass


class AnswerOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question_id: UUID
    text: str
    position: int
    is_correct: bool