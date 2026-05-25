from uuid import uuid4

import pytest

from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.question_attempt import QuestionResultStatus
from app.domain.exceptions import InvalidQuestionError


def test_question_is_created_with_valid_data() -> None:
    question = Question(
        id=uuid4(),
        section_id=uuid4(),
        text='What does GET usually do?',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        max_attempts=2,
        reward_points=5,
    )

    assert question.text == 'What does GET usually do?'
    assert question.max_attempts == 2
    assert question.reward_points == 5


def test_question_raises_error_when_text_is_blank() -> None:
    with pytest.raises(InvalidQuestionError):
        Question(
            id=uuid4(),
            section_id=uuid4(),
            text='   ',
            position=1,
        )


def test_single_choice_question_requires_exactly_one_correct_option() -> None:
    question = Question(
        id=uuid4(),
        section_id=uuid4(),
        text='Choose one',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
    )
    options = [
        AnswerOption(id=uuid4(), question_id=question.id, text='A', position=1, is_correct=True),
        AnswerOption(id=uuid4(), question_id=question.id, text='B', position=2, is_correct=True),
    ]

    with pytest.raises(InvalidQuestionError):
        question.validate_answer_options_configuration(options)


def test_question_resolves_correct_status_and_points() -> None:
    correct_option_id = uuid4()
    wrong_option_id = uuid4()
    question = Question(
        id=uuid4(),
        section_id=uuid4(),
        text='What method reads a resource?',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        answer_option_ids=[wrong_option_id, correct_option_id],
        reward_points=5,
    )
    options = [
        AnswerOption(id=wrong_option_id, question_id=question.id, text='POST', position=1, is_correct=False),
        AnswerOption(id=correct_option_id, question_id=question.id, text='GET', position=2, is_correct=True),
    ]

    assert question.resolve_result_status([correct_option_id], options) is QuestionResultStatus.CORRECT
    assert question.resolve_awarded_points([correct_option_id], options) == 5
    assert question.resolve_awarded_points([wrong_option_id], options) == 0