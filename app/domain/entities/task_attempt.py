from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidTaskAttemptError


class TaskAttemptStatus(StrEnum):
    PENDING = 'pending'
    CORRECT = 'correct'
    INCORRECT = 'incorrect'


@dataclass(slots=True)
class TaskAttempt:
    id: UUID
    task_id: UUID
    student_id: UUID
    submitted_answer: str
    attempt_number: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: TaskAttemptStatus = TaskAttemptStatus.PENDING
    awarded_points: int | None = None
    checked_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.submitted_answer or not self.submitted_answer.strip():
            raise InvalidTaskAttemptError('Task attempt answer cannot be empty.')
        if self.attempt_number < 1:
            raise InvalidTaskAttemptError('Task attempt number must be positive.')
        if self.awarded_points is not None and self.awarded_points < 0:
            raise InvalidTaskAttemptError('Awarded points cannot be negative.')

    def is_first_attempt(self) -> bool:
        return self.attempt_number == 1

    def is_repeat_attempt(self) -> bool:
        return self.attempt_number > 1

    def is_pending(self) -> bool:
        return self.status is TaskAttemptStatus.PENDING

    def is_correct(self) -> bool:
        return self.status is TaskAttemptStatus.CORRECT

    def is_incorrect(self) -> bool:
        return self.status is TaskAttemptStatus.INCORRECT

    def has_result(self) -> bool:
        return self.status is not TaskAttemptStatus.PENDING

    def apply_result(
            self,
            status: TaskAttemptStatus,
            awarded_points: int,
    ) -> None:
        if self.has_result():
            raise InvalidTaskAttemptError('Task attempt result is already defined.')
        if status is TaskAttemptStatus.PENDING:
            raise InvalidTaskAttemptError('Pending status cannot be applied as a final result.')
        if awarded_points < 0:
            raise InvalidTaskAttemptError('Awarded points cannot be negative.')
        if status is TaskAttemptStatus.INCORRECT and awarded_points != 0:
            raise InvalidTaskAttemptError(
                'Incorrect task attempt cannot have awarded points.'
            )

        self.status = status
        self.awarded_points = awarded_points
        self.checked_at = datetime.now(UTC)
