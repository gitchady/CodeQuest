from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.task_attempt_repository import TaskAttemptRepository
from app.domain.entities.task_attempt import TaskAttempt
from app.infrastructure.database.mappers.task_attempt_mapper import TaskAttemptMapper
from app.infrastructure.database.models.task_attempt_model import TaskAttemptModel


class SqlAlchemyTaskAttemptRepository(TaskAttemptRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, attempt_id: UUID) -> TaskAttempt | None:
        stmt = select(TaskAttemptModel).where(TaskAttemptModel.id == str(attempt_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else TaskAttemptMapper.to_domain(model)

    async def list_by_task_id(self, task_id: UUID) -> list[TaskAttempt]:
        stmt = (
            select(TaskAttemptModel)
            .where(TaskAttemptModel.task_id == str(task_id))
            .order_by(TaskAttemptModel.attempt_number)
        )
        result = await self.session.execute(stmt)
        return [TaskAttemptMapper.to_domain(model) for model in result.scalars().all()]

    async def get_by_student_and_task(
        self,
        student_id: UUID,
        task_id: UUID,
    ) -> list[TaskAttempt]:
        stmt = (
            select(TaskAttemptModel)
            .where(
                TaskAttemptModel.student_id == str(student_id),
                TaskAttemptModel.task_id == str(task_id),
            )
            .order_by(TaskAttemptModel.attempt_number)
        )
        result = await self.session.execute(stmt)
        return [TaskAttemptMapper.to_domain(model) for model in result.scalars().all()]

    async def exists_by_task_id(self, task_id: UUID) -> bool:
        stmt = (
            select(TaskAttemptModel.id)
            .where(TaskAttemptModel.task_id == str(task_id))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add(self, attempt: TaskAttempt) -> None:
        self.session.add(TaskAttemptMapper.to_model(attempt))
        await self.session.flush()

    async def update(self, attempt: TaskAttempt) -> None:
        model = await self.session.get(TaskAttemptModel, str(attempt.id))
        if model is None:
            return

        model.status = str(attempt.status)
        model.awarded_points = attempt.awarded_points
        model.checked_at = attempt.checked_at
        await self.session.flush()