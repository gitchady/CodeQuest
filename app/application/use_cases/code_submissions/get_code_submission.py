from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeSubmissionNotFoundError, PermissionDeniedError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.user import User


@dataclass(slots=True)
class GetCodeSubmissionCommand:
    actor: User
    submission_id: UUID


class GetCodeSubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: GetCodeSubmissionCommand) -> CodeSubmission:
        async with self.uow:
            submission = await self.uow.code_submissions.get_by_id(command.submission_id)
            if submission is None:
                raise CodeSubmissionNotFoundError('CodeSubmission not found.')

            if submission.student_id != command.actor.id:
                raise PermissionDeniedError('User cannot access this code submission.')

            return submission