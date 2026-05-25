from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeSubmissionNotFoundError, CodeTaskNotFoundError
from app.application.interfaces.code_execution_gateway import CodeExecutionGateway
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.code_submissions.complete_code_submission import (
    CompleteCodeSubmissionCommand,
    CompleteCodeSubmissionUseCase,
)


@dataclass(slots=True)
class ProcessCodeSubmissionCommand:
    submission_id: UUID


class ProcessCodeSubmissionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        execution_gateway: CodeExecutionGateway,
        complete_use_case: CompleteCodeSubmissionUseCase,
    ) -> None:
        self.uow = uow
        self.execution_gateway = execution_gateway
        self.complete_use_case = complete_use_case

    async def execute(self, command: ProcessCodeSubmissionCommand) -> None:
        async with self.uow:
            submission = await self.uow.code_submissions.get_by_id(command.submission_id)
            if submission is None:
                raise CodeSubmissionNotFoundError('CodeSubmission not found.')

            code_task = await self.uow.code_tasks.get_by_id(submission.code_task_id)
            if code_task is None:
                raise CodeTaskNotFoundError('CodeTask not found.')

            test_cases = await self.uow.test_cases.list_by_code_task_id(code_task.id)

            if submission.status.value == 'pending':
                submission.mark_running()
                await self.uow.code_submissions.update(submission)
                await self.uow.commit()

        result = await self.execution_gateway.execute(code_task, submission, test_cases)

        await self.complete_use_case.execute(
            CompleteCodeSubmissionCommand(
                submission_id=submission.id,
                status=result.status,
                passed_test_cases=result.passed_test_cases,
                total_test_cases=result.total_test_cases,
                stdout=result.stdout,
                stderr=result.stderr,
                error_message=result.error_message,
                exit_code=result.exit_code,
            )
        )