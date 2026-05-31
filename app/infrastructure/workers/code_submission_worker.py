from uuid import UUID

from app.application.use_cases.code_submissions.process_code_submission import (
    ProcessCodeSubmissionCommand,
    ProcessCodeSubmissionUseCase,
)


async def process_code_submission(
    submission_id: UUID,
    process_use_case: ProcessCodeSubmissionUseCase,
) -> None:
    await process_use_case.execute(
        ProcessCodeSubmissionCommand(submission_id=submission_id)
    )
