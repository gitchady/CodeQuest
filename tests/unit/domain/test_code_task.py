from uuid import uuid4

import pytest

from app.domain.entities.code_submission import CodeSubmissionStatus
from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus
from app.domain.exceptions import (
    CodeSubmissionLimitExceededError,
    InvalidCodeTaskError,
)


def build_code_task() -> CodeTask:
    return CodeTask(
        id=uuid4(),
        section_id=uuid4(),
        title='Sum two numbers',
        statement='Read two integers and print their sum.',
        position=1,
        language=CodeTaskLanguage.PYTHON,
        starter_code='print(1)',
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )


def test_code_task_creates_submission() -> None:
    task = build_code_task()

    submission = task.create_submission(
        student_id=uuid4(),
        source_code='print(1)',
        existing_submissions_count=0,
        has_passed_submission=False,
    )

    assert submission.attempt_number == 1
    assert submission.status is CodeSubmissionStatus.PENDING


def test_code_task_respects_submission_limit() -> None:
    task = build_code_task()

    with pytest.raises(CodeSubmissionLimitExceededError):
        task.create_submission(
            student_id=uuid4(),
            source_code='print(1)',
            existing_submissions_count=2,
            has_passed_submission=False,
        )


def test_code_submission_transitions_to_passed() -> None:
    task = build_code_task()
    submission = task.create_submission(
        student_id=uuid4(),
        source_code='print(1)',
        existing_submissions_count=0,
        has_passed_submission=False,
    )

    submission.mark_running()
    submission.apply_execution_result(
        ExecutionResult(
            submission_id=submission.id,
            status=ExecutionStatus.PASSED,
            passed_test_cases=2,
            total_test_cases=2,
            exit_code=0,
        )
    )

    assert submission.status is CodeSubmissionStatus.PASSED


def test_code_task_rejects_too_small_memory_limit() -> None:
    with pytest.raises(InvalidCodeTaskError):
        CodeTask(
            id=uuid4(),
            section_id=uuid4(),
            title='Bad config',
            statement='Invalid task.',
            position=1,
            language=CodeTaskLanguage.PYTHON,
            starter_code='print(1)',
            max_attempts=1,
            reward_points=1,
            time_limit_seconds=1,
            memory_limit_mb=8,
        )