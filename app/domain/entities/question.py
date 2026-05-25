from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID
from collections.abc import Sequence

from app.domain.entities.answer_option import AnswerOption
from app.domain.exceptions import (
    InvalidQuestionError,
    QuestionAlreadySolvedError,
    QuestionAttemptLimitExceededError,
    InvalidQuestionResultError
)

from app.domain.entities.question_attempt import QuestionResultStatus


class QuestionType(StrEnum):
    SINGLE_CHOICE = 'single_choice'
    MULTIPLE_CHOICE = 'multiple_choice'


@dataclass(slots=True)
class Question:
    id: UUID
    section_id: UUID
    text: str
    position: int
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    answer_option_ids: list[UUID] = field(default_factory=list)
    max_attempts: int = 1
    reward_points: int = 1

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.text or not self.text.strip():
            raise InvalidQuestionError('Question text cannot be empty.')
        if self.position < 1:
            raise InvalidQuestionError('Question position must be positive.')
        if self.max_attempts < 1:
            raise InvalidQuestionError('Question max_attempts must be positive.')
        if self.reward_points < 1:
            raise InvalidQuestionError('Question reward_points must be positive.')

    def update(
            self,
            text: str,
            position: int,
            question_type: QuestionType,
            max_attempts: int,
            reward_points: int,
    ) -> None:
        self.text = text
        self.position = position
        self.question_type = question_type
        self.max_attempts = max_attempts
        self.reward_points = reward_points
        self._validate()

    def add_answer_option(self, answer_option_id: UUID) -> None:
        if answer_option_id not in self.answer_option_ids:
            self.answer_option_ids.append(answer_option_id)

    def remove_answer_option(self, answer_option_id: UUID) -> None:
        if answer_option_id in self.answer_option_ids:
            self.answer_option_ids.remove(answer_option_id)

    def has_answer_options(self) -> bool:
        return bool(self.answer_option_ids)

    def is_single_choice(self) -> bool:
        return self.question_type is QuestionType.SINGLE_CHOICE

    def is_multiple_choice(self) -> bool:
        return self.question_type is QuestionType.MULTIPLE_CHOICE

    def allows_multiple_answers(self) -> bool:
        return self.is_multiple_choice()

    def validate_answer_options_configuration(
            self,
            answer_options: Sequence[AnswerOption],
    ) -> None:
        if len(answer_options) < 2:
            raise InvalidQuestionError('Question must have at least two answer options.')

        correct_options_count = sum(1 for option in answer_options if option.is_correct)
        if correct_options_count == 0:
            raise InvalidQuestionError('Question must have at least one correct answer option.')

        if self.is_single_choice() and correct_options_count != 1:
            raise InvalidQuestionError(
                'Single choice question must have exactly one correct answer option.'
            )

        if self.is_multiple_choice() and correct_options_count < 2:
            raise InvalidQuestionError(
                'Multiple choice question must have at least two correct answer options.'
            )

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
            raise QuestionAlreadySolvedError('Question has already been answered correctly.')
        if not self.can_start_attempt(existing_attempts_count):
            raise QuestionAttemptLimitExceededError('Question attempt limit has been reached.')

    def is_correct_selection(
            self,
            selected_option_ids: Sequence[UUID],
            answer_options: Sequence[AnswerOption],
    ) -> bool:
        expected_option_ids = set(self.answer_option_ids)
        actual_option_ids = {option.id for option in answer_options}
        selected_ids = set(selected_option_ids)

        if actual_option_ids != expected_option_ids:
            raise InvalidQuestionResultError(
                'Answer options do not match question configuration.'
            )

        if not selected_ids.issubset(actual_option_ids):
            raise InvalidQuestionResultError('Selected options contain unknown ids.')

        correct_option_ids = {option.id for option in answer_options if option.is_correct}
        return selected_ids == correct_option_ids

    def resolve_result_status(
            self,
            selected_option_ids: Sequence[UUID],
            answer_options: Sequence[AnswerOption],
    ) -> QuestionResultStatus:
        if self.is_correct_selection(selected_option_ids, answer_options):
            return QuestionResultStatus.CORRECT
        return QuestionResultStatus.INCORRECT

    def resolve_awarded_points(
            self,
            selected_option_ids: Sequence[UUID],
            answer_options: Sequence[AnswerOption],
    ) -> int:
        if self.is_correct_selection(selected_option_ids, answer_options):
            return self.reward_points
        return 0
