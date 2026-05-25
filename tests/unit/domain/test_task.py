from uuid import uuid4

import pytest

from app.domain.entities.task import Task, TaskCheckType
from app.domain.entities.task_attempt import TaskAttemptStatus
from app.domain.exceptions import (
    InvalidTaskError,
    TaskAlreadySolvedError,
    TaskAttemptLimitExceededError,
)


def build_exact_task() -> Task:
    return Task(
        id=uuid4(),
        section_id=uuid4(),
        title='HTTP method',
        statement='Enter the HTTP method used for reading a resource.',
        position=1,
        check_type=TaskCheckType.EXACT_MATCH,
        expected_answer='GET',
        max_attempts=2,
        reward_points=3,
    )


def test_exact_match_task_accepts_correct_answer() -> None:
    task = build_exact_task()

    assert task.is_correct_answer('GET') is True
    assert task.is_correct_answer(' GET ') is True
    assert task.is_correct_answer('POST') is False


def test_any_of_task_requires_non_empty_answers() -> None:
    with pytest.raises(InvalidTaskError):
        Task(
            id=uuid4(),
            section_id=uuid4(),
            title='HTTP status',
            statement='Enter one valid success code.',
            position=1,
            check_type=TaskCheckType.ANY_OF,
            accepted_answers=[],
            max_attempts=1,
            reward_points=1,
        )


def test_task_creates_attempt_with_incremented_number() -> None:
    task = build_exact_task()

    attempt = task.create_attempt(
        student_id=uuid4(),
        submitted_answer='GET',
        existing_attempts_count=1,
        has_correct_attempt=False,
    )

    assert attempt.attempt_number == 2
    assert attempt.status is TaskAttemptStatus.PENDING


def test_task_rejects_attempt_after_success() -> None:
    task = build_exact_task()

    with pytest.raises(TaskAlreadySolvedError):
        task.create_attempt(
            student_id=uuid4(),
            submitted_answer='GET',
            existing_attempts_count=1,
            has_correct_attempt=True,
        )


def test_task_rejects_attempt_after_limit() -> None:
    task = build_exact_task()

    with pytest.raises(TaskAttemptLimitExceededError):
        task.create_attempt(
            student_id=uuid4(),
            submitted_answer='GET',
            existing_attempts_count=2,
            has_correct_attempt=False,
        )