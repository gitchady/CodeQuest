from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.code_task import CodeTaskLanguage
from app.domain.entities.user import User
from app.application.exceptions import CodeTaskAlreadyUsedError, CodeTaskNotFoundError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.services.course_access_service import CourseAccessService
from app.domain.entities.code_task import CodeTask
from app.domain.exceptions import InvalidCodeTaskError


@dataclass(slots=True)
class UpdateCodeTaskCommand:
    actor: User
    code_task_id: UUID
    title: str
    statement: str
    position: int
    language: CodeTaskLanguage
    starter_code: str = ''
    max_attempts: int = 1
    reward_points: int = 1
    time_limit_seconds: int = 2
    memory_limit_mb: int = 128




class UpdateCodeTaskUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
        self.course_access_service = CourseAccessService(uow)

    async def execute(self, command: UpdateCodeTaskCommand) -> CodeTask:
        async with self.uow:
            code_task = await self.uow.code_tasks.get_by_id(command.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError('CodeTask not found.')

            await self.course_access_service.ensure_can_manage_section(
                actor=command.actor,
                section_id=code_task.section_id,
            )

            has_submissions = await self.uow.code_submissions.exists_by_code_task_id(code_task.id)

            execution_changed = (
                code_task.language is not command.language
                or code_task.time_limit_seconds != command.time_limit_seconds
                or code_task.memory_limit_mb != command.memory_limit_mb
            )
            learning_changed = (
                code_task.max_attempts != command.max_attempts
                or code_task.reward_points != command.reward_points
            )

            if execution_changed:
                try:
                    code_task.ensure_execution_policy_can_be_changed(has_submissions)
                except InvalidCodeTaskError as exc:
                    raise CodeTaskAlreadyUsedError(str(exc)) from exc

            if learning_changed:
                try:
                    code_task.ensure_learning_policy_can_be_changed(has_submissions)
                except InvalidCodeTaskError as exc:
                    raise CodeTaskAlreadyUsedError(str(exc)) from exc

            code_task.update_content(
                title=command.title,
                statement=command.statement,
                position=command.position,
                starter_code=command.starter_code,
            )

            if execution_changed:
                code_task.update_execution_policy(
                    language=command.language,
                    time_limit_seconds=command.time_limit_seconds,
                    memory_limit_mb=command.memory_limit_mb,
                )

            if learning_changed:
                code_task.update_learning_policy(
                    max_attempts=command.max_attempts,
                    reward_points=command.reward_points,
                )

            await self.uow.code_tasks.update(code_task)
            await self.uow.commit()
            return code_task