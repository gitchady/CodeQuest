from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.question_attempt_repository import \
    QuestionAttemptRepository
from app.domain.entities.question_attempt import QuestionAttempt
from app.infrastructure.database.mappers.question_attempt_mapper import QuestionAttemptMapper
from app.infrastructure.database.models.question_attempt_model import QuestionAttemptModel


class SqlAlchemyQuestionAttemptRepository(QuestionAttemptRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, attempt_id: UUID) -> QuestionAttempt | None:
        stmt = select(QuestionAttemptModel).where(QuestionAttemptModel.id == str(attempt_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else QuestionAttemptMapper.to_domain(model)

    async def get_by_student_and_question(
            self,
            student_id: UUID,
            question_id: UUID,
    ) -> list[QuestionAttempt]:
        stmt = (
            select(QuestionAttemptModel)
            .where(
                QuestionAttemptModel.student_id == str(student_id),
                QuestionAttemptModel.question_id == str(question_id),
            )
            .order_by(QuestionAttemptModel.attempt_number)
        )
        result = await self.session.execute(stmt)
        return [QuestionAttemptMapper.to_domain(model) for model in result.scalars().all()]

    async def exists_by_question_id(self, question_id: UUID) -> bool:
        stmt = (
            select(QuestionAttemptModel.id)
            .where(QuestionAttemptModel.question_id == str(question_id))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add(self, attempt: QuestionAttempt) -> None:
        self.session.add(QuestionAttemptMapper.to_model(attempt))
        await self.session.flush()