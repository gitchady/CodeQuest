from dataclasses import dataclass, field
from uuid import UUID

from app.domain.entities.question import QuestionType


@dataclass(slots=True)
class AnswerOptionDetailsDTO:
    id: UUID
    text: str
    position: int


@dataclass(slots=True)
class QuestionDetailsDTO:
    id: UUID
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType
    max_attempts: int
    reward_points: int
    answer_options: list[AnswerOptionDetailsDTO] = field(default_factory=list)