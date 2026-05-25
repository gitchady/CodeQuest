from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.interfaces.repositories.question_repository import QuestionRepository
from app.domain.entities.question import Question
from app.infrastructure.database.mappers.question_mapper import QuestionMapper
from app.infrastructure.database.models.question_model import QuestionModel


class SqlAlchemyQuestionRepository(QuestionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, question_id: UUID) -> Question | None:
        stmt = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answer_options))
            .where(QuestionModel.id == str(question_id))
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else QuestionMapper.to_domain(model)

    async def get_by_ids(self, question_ids: list[UUID]) -> list[Question]:
        if not question_ids:
            return []

        stmt = (
            select(QuestionModel)
            .options(selectinload(QuestionModel.answer_options))
            .where(QuestionModel.id.in_([str(item) for item in question_ids]))
        )
        result = await self.session.execute(stmt)
        return [QuestionMapper.to_domain(model) for model in result.scalars().all()]

    async def add(self, question: Question) -> None:
        self.session.add(QuestionMapper.to_model(question))
        await self.session.flush()

    async def update(self, question: Question) -> None:
        model = await self.session.get(QuestionModel, str(question.id))
        if model is None:
            return

        model.text = question.text
        model.position = question.position
        model.question_type = str(question.question_type)
        model.max_attempts = question.max_attempts
        model.reward_points = question.reward_points
        await self.session.flush()

    async def remove(self, question_id: UUID) -> None:
        model = await self.session.get(QuestionModel, str(question_id))
        if model is None:
            return

        await self.session.delete(model)
        await self.session.flush()