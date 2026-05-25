from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.exceptions import InvalidExecutionResultError


class ExecutionStatus(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    PASSED = 'passed'
    FAILED = 'failed'
    ERROR = 'error'


@dataclass(slots=True)
class ExecutionResult:
    submission_id: UUID
    status: ExecutionStatus
    passed_test_cases: int = 0
    total_test_cases: int = 0
    stdout: str = ''
    stderr: str = ''
    error_message: str = ''
    exit_code: int | None = None

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.passed_test_cases < 0:
            raise InvalidExecutionResultError(
                'ExecutionResult passed_test_cases cannot be negative.'
            )
        if self.total_test_cases < 0:
            raise InvalidExecutionResultError(
                'ExecutionResult total_test_cases cannot be negative.'
            )
        if self.passed_test_cases > self.total_test_cases:
            raise InvalidExecutionResultError(
                'ExecutionResult passed_test_cases cannot exceed total_test_cases.'
            )

        if self.status is ExecutionStatus.PASSED and self.total_test_cases == 0:
            raise InvalidExecutionResultError(
                'Passed execution result must contain test cases.'
            )
        if self.status is ExecutionStatus.PASSED and self.passed_test_cases != self.total_test_cases:
            raise InvalidExecutionResultError(
                'Passed execution result must pass all test cases.'
            )
        if self.status is ExecutionStatus.ERROR and not self.error_message.strip():
            raise InvalidExecutionResultError(
                'Error execution result must contain error_message.'
            )

    def is_final(self) -> bool:
        return self.status in {
            ExecutionStatus.PASSED,
            ExecutionStatus.FAILED,
            ExecutionStatus.ERROR,
        }

    def is_successful(self) -> bool:
        return self.status is ExecutionStatus.PASSED