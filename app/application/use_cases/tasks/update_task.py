from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import TaskAlreadyUsedError, TaskNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.task import Task, TaskCheckType
from app.domain.entities.user import User


@dataclass(slots=True)
class UpdateTaskCommand:
    actor: User
    task_id: UUID
    title: str
    statement: str
    position: int
    check_type: TaskCheckType
    expected_answer: str = ''
    accepted_answers: list[str] | None = None
    answer_pattern: str = ''
    max_attempts: int = 1
    reward_points: int = 1


class UpdateTaskUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateTaskCommand) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_by_id(command.task_id)
            if task is None:
                raise TaskNotFoundError('Task not found.')

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=task.section_id,
            )

            has_attempts = await self.uow.task_attempts.exists_by_task_id(task.id)

            checking_changed = (
                    task.check_type is not command.check_type
                    or task.expected_answer != command.expected_answer
                    or task.accepted_answers != (command.accepted_answers or [])
                    or task.answer_pattern != command.answer_pattern
            )
            policy_changed = (
                    task.max_attempts != command.max_attempts
                    or task.reward_points != command.reward_points
            )

            if has_attempts and (checking_changed or policy_changed):
                raise TaskAlreadyUsedError(
                    'Task already has student attempts and cannot be reconfigured safely.'
                )

            task.update(
                title=command.title,
                statement=command.statement,
                position=command.position,
                check_type=command.check_type,
                expected_answer=command.expected_answer,
                accepted_answers=command.accepted_answers,
                answer_pattern=command.answer_pattern,
                max_attempts=command.max_attempts,
                reward_points=command.reward_points,
            )

            await self.uow.tasks.update(task)
            await self.uow.commit()
            return task
