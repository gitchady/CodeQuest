from uuid import UUID

from app.domain.entities.answer_option import AnswerOption
from app.infrastructure.database.models.answer_option_model import AnswerOptionModel


class AnswerOptionMapper:
    @staticmethod
    def to_domain(model: AnswerOptionModel) -> AnswerOption:
        return AnswerOption(
            id=UUID(model.id),
            question_id=UUID(model.question_id),
            text=model.text,
            position=model.position,
            is_correct=model.is_correct,
        )

    @staticmethod
    def to_model(entity: AnswerOption) -> AnswerOptionModel:
        return AnswerOptionModel(
            id=str(entity.id),
            question_id=str(entity.question_id),
            text=entity.text,
            position=entity.position,
            is_correct=entity.is_correct,
        )