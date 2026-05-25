from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.entities.test_case import TestCase
from app.domain.entities.code_submission import CodeSubmission
from app.domain.exceptions import InvalidCodeTaskError, CodeTaskAlreadySolvedError, \
    CodeSubmissionLimitExceededError


class CodeTaskLanguage(StrEnum):
    PYTHON = 'python'
    JAVA = 'java'


@dataclass(slots=True)
class CodeTask:
    id: UUID
    section_id: UUID
    title: str
    statement: str
    position: int
    language: CodeTaskLanguage = CodeTaskLanguage.PYTHON
    starter_code: str = ''
    max_attempts: int = 1
    reward_points: int = 1
    time_limit_seconds: int = 2
    memory_limit_mb: int = 128
    test_case_ids: list[UUID] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidCodeTaskError('CodeTask title cannot be empty.')
        if not self.statement or not self.statement.strip():
            raise InvalidCodeTaskError('CodeTask statement cannot be empty.')
        if self.position < 1:
            raise InvalidCodeTaskError('CodeTask position must be positive.')
        if self.max_attempts < 1:
            raise InvalidCodeTaskError('CodeTask max_attempts must be positive.')
        if self.reward_points < 1:
            raise InvalidCodeTaskError('CodeTask reward_points must be positive.')
        if self.time_limit_seconds < 1:
            raise InvalidCodeTaskError('CodeTask time_limit_seconds must be positive.')
        if self.memory_limit_mb < 16:
            raise InvalidCodeTaskError('CodeTask memory_limit_mb is too small.')

    def update_content(
            self,
            title: str,
            statement: str,
            position: int,
            starter_code: str,
    ) -> None:
        self.title = title
        self.statement = statement
        self.position = position
        self.starter_code = starter_code
        self._validate()

    def update_learning_policy(self, max_attempts: int, reward_points: int) -> None:
        self.max_attempts = max_attempts
        self.reward_points = reward_points
        self._validate()

    def update_execution_policy(
            self,
            language: CodeTaskLanguage,
            time_limit_seconds: int,
            memory_limit_mb: int,
    ) -> None:
        self.language = language
        self.time_limit_seconds = time_limit_seconds
        self.memory_limit_mb = memory_limit_mb
        self._validate()

    def allows_multiple_attempts(self) -> bool:
        return self.max_attempts > 1

    def is_single_attempt(self) -> bool:
        return self.max_attempts == 1

    def requires_submission(self) -> bool:
        return True

    def requires_external_check(self) -> bool:
        return True

    def supports_inline_answer_check(self) -> bool:
        return False

    def requires_test_case_execution(self) -> bool:
        return True

    def can_start_submission(
            self,
            existing_submissions_count: int,
            has_passed_submission: bool = False,
    ) -> bool:
        if has_passed_submission:
            return False
        return existing_submissions_count < self.max_attempts

    def ensure_submission_available(
            self,
            existing_submissions_count: int,
            has_passed_submission: bool = False,
    ) -> None:
        if has_passed_submission:
            raise CodeTaskAlreadySolvedError('CodeTask has already been solved successfully.')
        if not self.can_start_submission(existing_submissions_count):
            raise CodeSubmissionLimitExceededError(
                'CodeTask submission limit has been reached.'
            )

    def next_submission_number(self, existing_submissions_count: int) -> int:
        if existing_submissions_count < 0:
            raise InvalidCodeTaskError('Existing submissions count cannot be negative.')
        return existing_submissions_count + 1

    def create_submission(
            self,
            student_id: UUID,
            source_code: str,
            existing_submissions_count: int,
            has_passed_submission: bool = False,
    ) -> CodeSubmission:
        self.ensure_submission_available(
            existing_submissions_count=existing_submissions_count,
            has_passed_submission=has_passed_submission,
        )

        return CodeSubmission(
            id=uuid4(),
            code_task_id=self.id,
            student_id=student_id,
            source_code=source_code,
            attempt_number=self.next_submission_number(existing_submissions_count),
        )

    def add_test_case(self, test_case_id: UUID) -> None:
        if test_case_id not in self.test_case_ids:
            self.test_case_ids.append(test_case_id)

    def remove_test_case(self, test_case_id: UUID) -> None:
        if test_case_id in self.test_case_ids:
            self.test_case_ids.remove(test_case_id)

    def has_test_cases(self) -> bool:
        return bool(self.test_case_ids)

    def create_test_case(
            self,
            position: int,
            input_data: str,
            expected_output: str,
            is_hidden: bool = True,
            explanation: str = '',
    ) -> TestCase:
        test_case = TestCase(
            id=uuid4(),
            code_task_id=self.id,
            position=position,
            input_data=input_data,
            expected_output=expected_output,
            is_hidden=is_hidden,
            explanation=explanation,
        )
        self.add_test_case(test_case.id)
        return test_case

    def ensure_execution_policy_can_be_changed(self, has_submissions: bool) -> None:
        if has_submissions:
            raise InvalidCodeTaskError(
                'CodeTask execution policy cannot be changed after submissions.'
            )

    def ensure_learning_policy_can_be_changed(self, has_submissions: bool) -> None:
        if has_submissions:
            raise InvalidCodeTaskError(
                'CodeTask learning policy cannot be changed after submissions.'
            )

    def ensure_test_cases_can_be_changed(self, has_submissions: bool) -> None:
        if has_submissions:
            raise InvalidCodeTaskError(
                'CodeTask test cases cannot be changed after submissions.'
            )
