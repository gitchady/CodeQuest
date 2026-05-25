from uuid import uuid4

import pytest

from app.domain.entities.question_attempt import QuestionAttempt, QuestionResultStatus
from app.domain.exceptions import InvalidQuestionAttemptError


def test_question_attempt_rejects_duplicate_selected_options() -> None:
    option_id = uuid4()

    with pytest.raises(InvalidQuestionAttemptError):
        QuestionAttempt(
            id=uuid4(),
            question_id=uuid4(),
            student_id=uuid4(),
            attempt_number=1,
            selected_option_ids=[option_id, option_id],
        )


def test_question_attempt_apply_result_sets_status_points_and_checked_at() -> None:
    attempt = QuestionAttempt(
        id=uuid4(),
        question_id=uuid4(),
        student_id=uuid4(),
        attempt_number=1,
        selected_option_ids=[uuid4()],
    )

    attempt.apply_result(
        result_status=QuestionResultStatus.CORRECT,
        awarded_points=5,
    )

    assert attempt.is_correct() is True
    assert attempt.awarded_points == 5
    assert attempt.checked_at is not None
