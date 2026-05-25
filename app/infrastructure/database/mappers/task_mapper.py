from uuid import UUID

from app.domain.entities.task import Task, TaskCheckType
from app.infrastructure.database.models.task_model import TaskModel


class TaskMapper:
    @staticmethod
    def to_domain(model: TaskModel) -> Task:
        return Task(
            id=UUID(model.id),
            section_id=UUID(model.section_id),
            title=model.title,
            statement=model.statement,
            position=model.position,
            check_type=TaskCheckType(model.check_type),
            expected_answer=model.expected_answer,
            accepted_answers=list(model.accepted_answers),
            answer_pattern=model.answer_pattern,
            max_attempts=model.max_attempts,
            reward_points=model.reward_points,
        )

    @staticmethod
    def to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=str(entity.id),
            section_id=str(entity.section_id),
            title=entity.title,
            statement=entity.statement,
            position=entity.position,
            check_type=str(entity.check_type),
            expected_answer=entity.expected_answer,
            accepted_answers=list(entity.accepted_answers),
            answer_pattern=entity.answer_pattern,
            max_attempts=entity.max_attempts,
            reward_points=entity.reward_points,
        )