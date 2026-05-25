from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.application.interfaces.repositories.code_task_repository import CodeTaskRepository
from app.domain.entities.code_task import CodeTask
from app.infrastructure.database.mappers.code_task_mapper import CodeTaskMapper
from app.infrastructure.database.models.code_task_model import CodeTaskModel


class SqlAlchemyCodeTaskRepository(CodeTaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, code_task: CodeTask) -> None:
        self.session.add(CodeTaskMapper.to_model(code_task))
        await self.session.flush()

    async def get_by_id(self, code_task_id: UUID) -> CodeTask | None:
        model = await self.session.get(CodeTaskModel, str(code_task_id))
        return None if model is None else CodeTaskMapper.to_domain(model)

    async def update(self, code_task: CodeTask) -> None:
        model = await self.session.get(CodeTaskModel, str(code_task.id))
        if model is None:
            return

        model.title = code_task.title
        model.statement = code_task.statement
        model.position = code_task.position
        model.language = str(code_task.language)
        model.starter_code = code_task.starter_code
        model.max_attempts = code_task.max_attempts
        model.reward_points = code_task.reward_points
        model.time_limit_seconds = code_task.time_limit_seconds
        model.memory_limit_mb = code_task.memory_limit_mb
        await self.session.flush()

    async def get_by_ids(self, code_task_ids: list[UUID]) -> list[CodeTask]:
        if not code_task_ids:
            return []

        stmt = select(CodeTaskModel).where(
            CodeTaskModel.id.in_([str(code_task_id) for code_task_id in code_task_ids])
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [CodeTaskMapper.to_domain(model) for model in models]
