from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.user import User
from app.application.exceptions import (
    CodeTaskNotFoundError,
    PermissionDeniedError,
    RetryableExecutionError,
)
from app.application.interfaces.submission_queue import SubmissionQueue
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.code_submission import CodeSubmission


@dataclass(slots=True)
class SubmitCodeSubmissionCommand:
    actor: User
    code_task_id: UUID
    source_code: str


class SubmitCodeSubmissionUseCase:
    def __init__(self, uow: UnitOfWork, submission_queue: SubmissionQueue) -> None:
        self.uow = uow
        self.submission_queue = submission_queue

    async def execute(self, command: SubmitCodeSubmissionCommand) -> CodeSubmission:
        if not command.actor.can_submit_task_solutions():
            raise PermissionDeniedError('User cannot submit code solutions.')

        async with self.uow:
            code_task = await self.uow.code_tasks.get_by_id(command.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError('CodeTask not found.')

            student_submissions = (
                await self.uow.code_submissions.list_by_code_task_and_student_id(
                    code_task_id=code_task.id,
                    student_id=command.actor.id,
                )
            )
            existing_submissions_count = len(student_submissions)
            has_passed_submission = any(
                submission.status.value == 'passed'
                for submission in student_submissions
            )

            submission = code_task.create_submission(
                student_id=command.actor.id,
                source_code=command.source_code,
                existing_submissions_count=existing_submissions_count,
                has_passed_submission=has_passed_submission,
            )

            await self.uow.code_submissions.add(submission)
            await self.uow.commit()

        try:
            await self.submission_queue.enqueue(submission.id)
        except Exception as exc:
            await self._mark_enqueue_failed(submission.id)
            raise RetryableExecutionError('Submission queue enqueue failed.') from exc
        return submission

    async def _mark_enqueue_failed(self, submission_id: UUID) -> None:
        async with self.uow:
            submission = await self.uow.code_submissions.get_by_id(submission_id)
            if submission is None:
                return

            if submission.status.value == 'pending':
                submission.mark_running()
                submission.mark_error()
                await self.uow.code_submissions.update(submission)
                await self.uow.commit()
