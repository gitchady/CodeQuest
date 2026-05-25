from uuid import uuid4

import pytest

from app.domain.entities.answer_option import AnswerOption
from app.domain.exceptions import InvalidAnswerOptionError


def test_answer_option_raises_error_when_text_is_blank() -> None:
    with pytest.raises(InvalidAnswerOptionError):
        AnswerOption(
            id=uuid4(),
            question_id=uuid4(),
            text='   ',
            position=1,
        )


def test_answer_option_update_changes_text_position_and_flag() -> None:
    option = AnswerOption(
        id=uuid4(),
        question_id=uuid4(),
        text='POST',
        position=1,
        is_correct=False,
    )

    option.update(text='GET', position=2, is_correct=True)

    assert option.text == 'GET'
    assert option.position == 2
    assert option.is_correct is True