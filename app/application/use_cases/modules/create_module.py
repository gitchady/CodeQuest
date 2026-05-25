from dataclasses import dataclass
from uuid import UUID, uuid4

from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.module import Module
from app.domain.entities.user import User


@dataclass(slots=True)
class CreateModuleCommand:
    actor: User
    course_id: UUID
    title: str
    description: str
    position: int


class CreateModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateModuleCommand) -> Module:
        async with self.uow:
            course = await self.course_access_service.ensure_can_manage_course(
                actor=command.actor,
                course_id=command.course_id,
            )

            module = Module(
                id=uuid4(),
                course_id=command.course_id,
                title=command.title,
                description=command.description,
                position=command.position,
            )
            course.add_module(module.id)
            await self.uow.modules.add(module)
            await self.uow.courses.update(course)
            await self.uow.commit()
            return module
