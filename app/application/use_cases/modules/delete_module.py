from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CourseNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteModuleCommand:
    actor: User
    module_id: UUID


class DeleteModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteModuleCommand) -> None:
        async with self.uow:
            module = await self.course_access_service.ensure_can_manage_module(
                actor=command.actor,
                module_id=command.module_id,
            )

            course = await self.uow.courses.get_by_id(module.course_id)
            if course is None:
                raise CourseNotFoundError("Course not found.")

            course.remove_module(module.id)
            await self.uow.courses.update(course)
            await self.uow.modules.remove(module.id)
            await self.uow.commit()
