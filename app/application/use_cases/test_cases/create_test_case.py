from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.user import User
from app.application.exceptions import CodeTaskNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.test_case import TestCase

@dataclass(slots=True)
class CreateTestCaseCommand:
    actor: User
    code_task_id: UUID
    position: int
    input_data: str
    expected_output: str
    is_hidden: bool = True
    explanation: str = ''


class CreateTestCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: CreateTestCaseCommand) -> TestCase:
        async with self.uow:
            code_task = await self.uow.code_tasks.get_by_id(command.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError('CodeTask not found.')

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id,
            )

            test_case = code_task.create_test_case(
                position=command.position,
                input_data=command.input_data,
                expected_output=command.expected_output,
                is_hidden=command.is_hidden,
                explanation=command.explanation,
            )

            await self.uow.test_cases.add(test_case)
            await self.uow.code_tasks.update(code_task)
            await self.uow.commit()
            return test_case