from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidQuestionAttemptError


class QuestionResultStatus(StrEnum):
    CORRECT = 'correct'
    INCORRECT = 'incorrect'


@dataclass(slots=True)
class QuestionAttempt:
    id: UUID
    question_id: UUID
    student_id: UUID
    attempt_number: int
    selected_option_ids: list[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    result_status: QuestionResultStatus | None = None
    awarded_points: int | None = None
    checked_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.attempt_number < 1:
            raise InvalidQuestionAttemptError('Question attempt number must be positive.')
        if not self.selected_option_ids:
            raise InvalidQuestionAttemptError(
                'Question attempt must contain at least one selected option.'
            )
        if len(self.selected_option_ids) != len(set(self.selected_option_ids)):
            raise InvalidQuestionAttemptError(
                'Question attempt cannot contain duplicate selected options.'
            )

    def is_first_attempt(self) -> bool:
        return self.attempt_number == 1

    def is_repeat_attempt(self) -> bool:
        return self.attempt_number > 1

    def has_selected_options(self) -> bool:
        return bool(self.selected_option_ids)

    def selected_options_count(self) -> int:
        return len(self.selected_option_ids)

    def uses_option(self, answer_option_id: UUID) -> bool:
        return answer_option_id in self.selected_option_ids

    def has_result(self) -> bool:
        return self.result_status is not None

    def is_correct(self) -> bool:
        return self.result_status is QuestionResultStatus.CORRECT

    def is_incorrect(self) -> bool:
        return self.result_status is QuestionResultStatus.INCORRECT

    def apply_result(
            self,
            result_status: QuestionResultStatus,
            awarded_points: int,
    ) -> None:
        if self.has_result():
            raise InvalidQuestionAttemptError('Question attempt result is already defined.')
        if awarded_points < 0:
            raise InvalidQuestionAttemptError('Awarded points cannot be negative.')
        if result_status is QuestionResultStatus.INCORRECT and awarded_points != 0:
            raise InvalidQuestionAttemptError(
                'Incorrect question attempt cannot have awarded points.'
            )

        self.result_status = result_status
        self.awarded_points = awarded_points
        self.checked_at = datetime.now(UTC)
