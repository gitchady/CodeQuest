from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.answer_option_repository import AnswerOptionRepository
from app.domain.entities.answer_option import AnswerOption
from app.infrastructure.database.mappers.answer_option_mapper import AnswerOptionMapper
from app.infrastructure.database.models.answer_option_model import AnswerOptionModel


class SqlAlchemyAnswerOptionRepository(AnswerOptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, answer_option_id: UUID) -> AnswerOption | None:
        stmt = select(AnswerOptionModel).where(AnswerOptionModel.id == str(answer_option_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else AnswerOptionMapper.to_domain(model)

    async def get_by_ids(self, answer_option_ids: list[UUID]) -> list[AnswerOption]:
        if not answer_option_ids:
            return []

        stmt = select(AnswerOptionModel).where(
            AnswerOptionModel.id.in_([str(item) for item in answer_option_ids])
        )
        result = await self.session.execute(stmt)
        return [AnswerOptionMapper.to_domain(model) for model in result.scalars().all()]

    async def add(self, answer_option: AnswerOption) -> None:
        self.session.add(AnswerOptionMapper.to_model(answer_option))
        await self.session.flush()

    async def update(self, answer_option: AnswerOption) -> None:
        model = await self.session.get(AnswerOptionModel, str(answer_option.id))
        if model is None:
            return

        model.text = answer_option.text
        model.position = answer_option.position
        model.is_correct = answer_option.is_correct
        await self.session.flush()

    async def remove(self, answer_option_id: UUID) -> None:
        model = await self.session.get(AnswerOptionModel, str(answer_option_id))
        if model is None:
            return

        await self.session.delete(model)
        await self.session.flush()