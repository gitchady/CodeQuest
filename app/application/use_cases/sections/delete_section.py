from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.user import User


@dataclass(slots=True)
class DeleteSectionCommand:
    actor: User
    section_id: UUID


class DeleteSectionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: DeleteSectionCommand) -> None:
        async with self.uow:
            section = await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=command.section_id,
            )

            module = await self.uow.modules.get_by_id(section.module_id)
            if module is None:
                raise ModuleNotFoundError("Module not found.")

            module.remove_section(section.id)
            await self.uow.modules.update(module)
            await self.uow.sections.remove(section.id)
            await self.uow.commit()
