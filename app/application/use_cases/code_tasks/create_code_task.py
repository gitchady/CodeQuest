from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.entities.code_task import CodeTaskLanguage
from app.domain.entities.user import User
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.code_task import CodeTask

@dataclass(slots=True)
class CreateCodeTaskCommand:
    actor: User
    section_id: UUID
    title: str
    statement: str
    position: int
    language: CodeTaskLanguage
    starter_code: str = ''
    max_attempts: int = 1
    reward_points: int = 1
    time_limit_seconds: int = 2
    memory_limit_mb: int = 128





class CreateCodeTaskUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateCodeTaskCommand) -> CodeTask:
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )

            code_task = CodeTask(
                id=uuid4(),
                section_id=section.id,
                title=command.title,
                statement=command.statement,
                position=command.position,
                language=command.language,
                starter_code=command.starter_code,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
                time_limit_seconds=command.time_limit_seconds,
                memory_limit_mb=command.memory_limit_mb,
            )

            section.add_code_task(code_task.id)
            await self.uow.code_tasks.add(code_task)
            await self.uow.sections.update(section)
            await self.uow.commit()
            return code_task