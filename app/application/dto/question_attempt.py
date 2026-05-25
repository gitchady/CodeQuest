from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.entities.question import QuestionType
from app.domain.entities.question_attempt import QuestionResultStatus


@dataclass(slots=True)
class QuestionAttemptAnswerOptionDTO:
    id: UUID
    text: str
    position: int


@dataclass(slots=True)
class StartQuestionAttemptDTO:
    question_id: UUID
    text: str
    question_type: QuestionType
    attempt_number: int
    max_attempts: int
    reward_points: int
    can_submit: bool
    is_solved: bool
    attempts_used: int
    selected_option_ids: list[UUID] = field(default_factory=list)
    last_result_status: QuestionResultStatus | None = None
    last_awarded_points: int | None = None
    answer_options: list[QuestionAttemptAnswerOptionDTO] = field(default_factory=list)



@dataclass(slots=True)
class QuestionAttemptResultDTO:
    attempt_id: UUID
    question_id: UUID
    attempt_number: int
    result_status: QuestionResultStatus
    awarded_points: int
    checked_at: datetime
    selected_option_ids: list[UUID]
