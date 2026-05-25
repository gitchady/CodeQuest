from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeTaskNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.user import User


@dataclass(slots=True)
class ListCodeSubmissionsCommand:
    actor: User
    code_task_id: UUID


class ListCodeSubmissionsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: ListCodeSubmissionsCommand) -> list[CodeSubmission]:
        async with self.uow:
            code_task = await self.uow.code_tasks.get_by_id(command.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError('CodeTask not found.')

            return await self.uow.code_submissions.list_by_code_task_and_student_id(
                code_task_id=code_task.id,
                student_id=command.actor.id,
            )
