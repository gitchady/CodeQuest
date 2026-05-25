from uuid import UUID

from app.domain.entities.question_attempt import QuestionAttempt, QuestionResultStatus
from app.infrastructure.database.models.question_attempt_model import QuestionAttemptModel


class QuestionAttemptMapper:
    @staticmethod
    def to_domain(model: QuestionAttemptModel) -> QuestionAttempt:
        return QuestionAttempt(
            id=UUID(model.id),
            question_id=UUID(model.question_id),
            student_id=UUID(model.student_id),
            attempt_number=model.attempt_number,
            selected_option_ids=[UUID(item) for item in model.selected_option_ids],
            created_at=model.created_at,
            result_status=(
                QuestionResultStatus(model.result_status)
                if model.result_status is not None
                else None
            ),
            awarded_points=model.awarded_points,
            checked_at=model.checked_at,
        )

    @staticmethod
    def to_model(entity: QuestionAttempt) -> QuestionAttemptModel:
        return QuestionAttemptModel(
            id=str(entity.id),
            question_id=str(entity.question_id),
            student_id=str(entity.student_id),
            attempt_number=entity.attempt_number,
            selected_option_ids=[str(item) for item in entity.selected_option_ids],
            created_at=entity.created_at,
            result_status=(
                str(entity.result_status)
                if entity.result_status is not None
                else None
            ),
            awarded_points=entity.awarded_points,
            checked_at=entity.checked_at,
        )