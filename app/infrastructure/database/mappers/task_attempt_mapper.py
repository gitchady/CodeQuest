from uuid import UUID

from app.domain.entities.task_attempt import TaskAttempt, TaskAttemptStatus
from app.infrastructure.database.models.task_attempt_model import TaskAttemptModel


class TaskAttemptMapper:
    @staticmethod
    def to_domain(model: TaskAttemptModel) -> TaskAttempt:
        return TaskAttempt(
            id=UUID(model.id),
            task_id=UUID(model.task_id),
            student_id=UUID(model.student_id),
            submitted_answer=model.submitted_answer,
            attempt_number=model.attempt_number,
            created_at=model.created_at,
            status=TaskAttemptStatus(model.status),
            awarded_points=model.awarded_points,
            checked_at=model.checked_at,
        )

    @staticmethod
    def to_model(entity: TaskAttempt) -> TaskAttemptModel:
        return TaskAttemptModel(
            id=str(entity.id),
            task_id=str(entity.task_id),
            student_id=str(entity.student_id),
            submitted_answer=entity.submitted_answer,
            attempt_number=entity.attempt_number,
            created_at=entity.created_at,
            status=str(entity.status),
            awarded_points=entity.awarded_points,
            checked_at=entity.checked_at,
        )