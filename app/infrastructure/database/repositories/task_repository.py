from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.task_repository import TaskRepository
from app.domain.entities.task import Task
from app.infrastructure.database.mappers.task_mapper import TaskMapper
from app.infrastructure.database.models.task_model import TaskModel


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, task_id: UUID) -> Task | None:
        stmt = select(TaskModel).where(TaskModel.id == str(task_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else TaskMapper.to_domain(model)

    async def add(self, task: Task) -> None:
        self.session.add(TaskMapper.to_model(task))
        await self.session.flush()

    async def update(self, task: Task) -> None:
        model = await self.session.get(TaskModel, str(task.id))
        if model is None:
            return

        model.title = task.title
        model.statement = task.statement
        model.position = task.position
        model.check_type = str(task.check_type)
        model.expected_answer = task.expected_answer
        model.accepted_answers = list(task.accepted_answers)
        model.answer_pattern = task.answer_pattern
        model.max_attempts = task.max_attempts
        model.reward_points = task.reward_points
        await self.session.flush()

    async def get_by_ids(self, task_ids: list[UUID]) -> list[Task]:
        if not task_ids:
            return []

        stmt = select(TaskModel).where(TaskModel.id.in_([str(task_id) for task_id in task_ids]))
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [TaskMapper.to_domain(model) for model in models]
