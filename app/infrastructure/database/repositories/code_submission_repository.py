from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.code_submission_repository import CodeSubmissionRepository
from app.domain.entities.code_submission import CodeSubmission
from app.infrastructure.database.mappers.code_submission_mapper import CodeSubmissionMapper
from app.infrastructure.database.models.code_submission_model import CodeSubmissionModel


class SqlAlchemyCodeSubmissionRepository(CodeSubmissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, submission: CodeSubmission) -> None:
        self.session.add(CodeSubmissionMapper.to_model(submission))
        await self.session.flush()

    async def get_by_id(self, submission_id: UUID) -> CodeSubmission | None:
        model = await self.session.get(CodeSubmissionModel, str(submission_id))
        return None if model is None else CodeSubmissionMapper.to_domain(model)

    async def update(self, submission: CodeSubmission) -> None:
        model = await self.session.get(CodeSubmissionModel, str(submission.id))
        if model is None:
            return

        model.status = submission.status.value
        model.started_at = submission.started_at
        model.finished_at = submission.finished_at
        await self.session.flush()

    async def list_by_code_task_id(self, code_task_id: UUID) -> list[CodeSubmission]:
        stmt = select(CodeSubmissionModel).where(
            CodeSubmissionModel.code_task_id == str(code_task_id)
        )
        result = await self.session.execute(stmt)
        return [CodeSubmissionMapper.to_domain(model) for model in result.scalars().all()]

    async def list_by_code_task_and_student_id(
        self,
        code_task_id: UUID,
        student_id: UUID,
    ) -> list[CodeSubmission]:
        stmt = select(CodeSubmissionModel).where(
            CodeSubmissionModel.code_task_id == str(code_task_id),
            CodeSubmissionModel.student_id == str(student_id),
        ).order_by(CodeSubmissionModel.attempt_number)
        result = await self.session.execute(stmt)
        return [CodeSubmissionMapper.to_domain(model) for model in result.scalars().all()]

    async def exists_by_code_task_id(self, code_task_id: UUID) -> bool:
        stmt = select(CodeSubmissionModel.id).where(
            CodeSubmissionModel.code_task_id == str(code_task_id)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
