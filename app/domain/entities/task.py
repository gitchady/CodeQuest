from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4
import re

from app.domain.entities.task_attempt import TaskAttempt
from app.domain.exceptions import (
    InvalidTaskError,
    TaskAlreadySolvedError,
    TaskAttemptLimitExceededError,
)


class TaskCheckType(StrEnum):
    EXACT_MATCH = 'exact_match'
    ANY_OF = 'any_of'
    REGEX = 'regex'


@dataclass(slots=True)
class Task:
    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    check_type: TaskCheckType = TaskCheckType.EXACT_MATCH
    expected_answer: str = ''
    accepted_answers: list[str] = field(default_factory=list)
    answer_pattern: str = ''
    max_attempts: int = 1
    reward_points: int = 1

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidTaskError('Task title cannot be empty.')
        if not self.statement or not self.statement.strip():
            raise InvalidTaskError('Task statement cannot be empty.')
        if self.position < 1:
            raise InvalidTaskError('Task position must be positive.')
        if self.max_attempts < 1:
            raise InvalidTaskError('Task max_attempts must be positive.')
        if self.reward_points < 1:
            raise InvalidTaskError('Task reward_points must be positive.')

        if self.check_type is TaskCheckType.EXACT_MATCH:
            if not self.expected_answer or not self.expected_answer.strip():
                raise InvalidTaskError('Exact-match task must define expected_answer.')

        if self.check_type is TaskCheckType.ANY_OF:
            if len(self.normalized_accepted_answers()) == 0:
                raise InvalidTaskError('Any-of task must define accepted_answers.')

        if self.check_type is TaskCheckType.REGEX:
            if not self.answer_pattern or not self.answer_pattern.strip():
                raise InvalidTaskError('Regex task must define answer_pattern.')
            try:
                re.compile(self.answer_pattern)
            except re.error as exc:
                raise InvalidTaskError('Task answer_pattern is invalid.') from exc

    def update(
            self,
            title: str,
            statement: str,
            position: int,
            check_type: TaskCheckType,
            expected_answer: str = '',
            accepted_answers: list[str] | None = None,
            answer_pattern: str = '',
            max_attempts: int = 1,
            reward_points: int = 1,
    ) -> None:
        self.title = title
        self.statement = statement
        self.position = position
        self.check_type = check_type
        self.expected_answer = expected_answer
        self.accepted_answers = accepted_answers or []
        self.answer_pattern = answer_pattern
        self.max_attempts = max_attempts
        self.reward_points = reward_points
        self._validate()

    def allows_multiple_attempts(self) -> bool:
        return self.max_attempts > 1

    def is_single_attempt(self) -> bool:
        return self.max_attempts == 1

    def requires_submission(self) -> bool:
        return True

    def can_start_attempt(
            self,
            existing_attempts_count: int,
            has_correct_attempt: bool = False,
    ) -> bool:
        if has_correct_attempt:
            return False
        return existing_attempts_count < self.max_attempts

    def ensure_attempt_available(
            self,
            existing_attempts_count: int,
            has_correct_attempt: bool = False,
    ) -> None:
        if has_correct_attempt:
            raise TaskAlreadySolvedError('Task has already been solved successfully.')
        if not self.can_start_attempt(existing_attempts_count):
            raise TaskAttemptLimitExceededError('Task attempt limit has been reached.')

    def normalize_answer(self, answer: str) -> str:
        return answer.strip()

    def is_correct_answer(self, answer: str) -> bool:
        normalized_actual = self.normalize_answer(answer)

        if self.check_type is TaskCheckType.EXACT_MATCH:
            normalized_expected = self.normalize_answer(self.expected_answer)
            return normalized_actual == normalized_expected

        if self.check_type is TaskCheckType.ANY_OF:
            return normalized_actual in self.normalized_accepted_answers()

        if self.check_type is TaskCheckType.REGEX:
            return re.fullmatch(self.answer_pattern, normalized_actual) is not None

        raise InvalidTaskError('Unsupported task check type.')

    def normalized_accepted_answers(self) -> list[str]:
        normalized: list[str] = []
        for item in self.accepted_answers:
            value = self.normalize_answer(item)
            if not value:
                continue
            if value not in normalized:
                normalized.append(value)
        return normalized

    def next_attempt_number(self, existing_attempts_count: int) -> int:
        if existing_attempts_count < 0:
            raise InvalidTaskError('Existing attempts count cannot be negative.')
        return existing_attempts_count + 1

    def create_attempt(
            self,
            student_id: UUID,
            submitted_answer: str,
            existing_attempts_count: int,
            has_correct_attempt: bool = False,
    ) -> TaskAttempt:
        self.ensure_attempt_available(
            existing_attempts_count=existing_attempts_count,
            has_correct_attempt=has_correct_attempt,
        )

        return TaskAttempt(
            id=uuid4(),
            task_id=self.id,
            student_id=student_id,
            submitted_answer=submitted_answer,
            attempt_number=self.next_attempt_number(existing_attempts_count),
        )
