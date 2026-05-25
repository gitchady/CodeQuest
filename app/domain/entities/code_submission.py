from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidCodeSubmissionError
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus

class CodeSubmissionStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    PASSED = 'passed'
    FAILED = 'failed'
    ERROR = 'error'


@dataclass(slots=True)
class CodeSubmission:
    id: UUID
    code_task_id: UUID
    student_id: UUID
    source_code: str
    attempt_number: int
    status: CodeSubmissionStatus = CodeSubmissionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.source_code or not self.source_code.strip():
            raise InvalidCodeSubmissionError('CodeSubmission source_code cannot be empty.')
        if self.attempt_number < 1:
            raise InvalidCodeSubmissionError('CodeSubmission attempt_number must be positive.')

    def mark_running(self) -> None:
        if self.status is not CodeSubmissionStatus.PENDING:
            raise InvalidCodeSubmissionError('Only pending submission can be started.')
        self.status = CodeSubmissionStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def mark_passed(self) -> None:
        if self.status is not CodeSubmissionStatus.RUNNING:
            raise InvalidCodeSubmissionError('Only running submission can be passed.')
        self.status = CodeSubmissionStatus.PASSED
        self.finished_at = datetime.now(UTC)

    def mark_failed(self) -> None:
        if self.status is not CodeSubmissionStatus.RUNNING:
            raise InvalidCodeSubmissionError('Only running submission can be failed.')
        self.status = CodeSubmissionStatus.FAILED
        self.finished_at = datetime.now(UTC)

    def mark_error(self) -> None:
        if self.status is not CodeSubmissionStatus.RUNNING:
            raise InvalidCodeSubmissionError('Only running submission can be completed with error.')
        self.status = CodeSubmissionStatus.ERROR
        self.finished_at = datetime.now(UTC)


    def apply_execution_result(self, result: ExecutionResult) -> None:
        if result.submission_id != self.id:
            raise InvalidCodeSubmissionError(
                'Execution result does not belong to this submission.'
            )
        if not result.is_final():
            raise InvalidCodeSubmissionError(
                'Only final execution result can be applied to submission.'
            )
        if self.status is not CodeSubmissionStatus.RUNNING:
            raise InvalidCodeSubmissionError(
                'Only running submission can accept final execution result.'
            )

        if result.status is ExecutionStatus.PASSED:
            self.mark_passed()
            return
        if result.status is ExecutionStatus.FAILED:
            self.mark_failed()
            return
        if result.status is ExecutionStatus.ERROR:
            self.mark_error()
            return

        raise InvalidCodeSubmissionError('Unsupported execution result status.')
