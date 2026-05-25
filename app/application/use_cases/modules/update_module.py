from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import ModuleNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.module import Module
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateModuleCommand:
    actor: User
    module_id: UUID
    title: str
    description: str
    position: int


class UpdateModuleUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateModuleCommand) -> Module:
        async with self.uow:
            module = await self.uow.modules.get_by_id(command.module_id)
            if module is None:
                raise ModuleNotFoundError('Module not found.')

            await self.course_access_service.ensure_can_manage_module(
                actor=command.actor,
                module_id=module.id,
            )

            module.update(
                title=command.title,
                description=command.description,
                position=command.position,
            )
            await self.uow.modules.update(module)
            await self.uow.commit()
            return module
