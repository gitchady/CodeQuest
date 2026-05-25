from uuid import UUID

from app.domain.entities.question import Question, QuestionType
from app.infrastructure.database.models.question_model import QuestionModel


class QuestionMapper:
    @staticmethod
    def to_domain(model: QuestionModel) -> Question:
        return Question(
            id=UUID(model.id),
            section_id=UUID(model.section_id),
            text=model.text,
            position=model.position,
            question_type=QuestionType(model.question_type),
            max_attempts=model.max_attempts,
            reward_points=model.reward_points,
            answer_option_ids=[UUID(option.id) for option in model.answer_options],
        )

    @staticmethod
    def to_model(entity: Question) -> QuestionModel:
        return QuestionModel(
            id=str(entity.id),
            section_id=str(entity.section_id),
            text=entity.text,
            position=entity.position,
            question_type=str(entity.question_type),
            max_attempts=entity.max_attempts,
            reward_points=entity.reward_points,
        )