from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.progress_repository import ProgressRepository
from app.domain.entities.progress import Progress
from app.infrastructure.database.mappers.progress_mapper import ProgressMapper
from app.infrastructure.database.models.progress_model import ProgressModel


class SqlAlchemyProgressRepository(ProgressRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_student_and_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> Progress | None:
        stmt = select(ProgressModel).where(
            ProgressModel.student_id == str(student_id),
            ProgressModel.course_id == str(course_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else ProgressMapper.to_domain(model)

    async def add(self, progress: Progress) -> None:
        self.session.add(ProgressMapper.to_model(progress))
        await self.session.flush()

    async def update(self, progress: Progress) -> None:
        model = await self.session.get(ProgressModel, str(progress.id))
        if model is None:
            return

        model.completed_question_ids = [str(item) for item in progress.completed_question_ids]
        model.completed_task_ids = [str(item) for item in progress.completed_task_ids]
        model.completed_code_task_ids = [str(item) for item in progress.completed_code_task_ids]
        model.completed_section_ids = [str(item) for item in progress.completed_section_ids]
        model.completed_module_ids = [str(item) for item in progress.completed_module_ids]
        model.total_points = progress.total_points
        await self.session.flush()
