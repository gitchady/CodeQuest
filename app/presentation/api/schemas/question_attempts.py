from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.question import QuestionType
from app.domain.entities.question_attempt import QuestionResultStatus


class QuestionAttemptAnswerOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    position: int


class StartQuestionAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: UUID
    text: str
    question_type: QuestionType
    attempt_number: int
    max_attempts: int
    reward_points: int
    can_submit: bool
    is_solved: bool
    attempts_used: int
    selected_option_ids: list[UUID] = Field(default_factory=list)
    last_result_status: QuestionResultStatus | None = None
    last_awarded_points: int | None = None
    answer_options: list[QuestionAttemptAnswerOptionResponse]


class SubmitQuestionAnswerRequest(BaseModel):
    selected_option_ids: list[UUID] = Field(min_length=1)


class QuestionAttemptResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: UUID
    question_id: UUID
    attempt_number: int
    result_status: QuestionResultStatus
    awarded_points: int
    checked_at: datetime
    selected_option_ids: list[UUID]