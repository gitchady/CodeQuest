from uuid import uuid4

import pytest

from app.application.exceptions import RetryableExecutionError
from app.infrastructure.workers.code_submission_worker import process_code_submission


class FakeProcessUseCase:
    def __init__(self) -> None:
        self.received_submission_ids = []

    async def execute(self, command) -> None:
        self.received_submission_ids.append(command.submission_id)





@pytest.mark.asyncio
async def test_process_code_submission_delegates_to_use_case() -> None:
    process_use_case = FakeProcessUseCase()
    submission_id = uuid4()

    await process_code_submission(
        submission_id=submission_id,
        process_use_case=process_use_case,
    )

    assert process_use_case.received_submission_ids == [submission_id]


class RetryableProcessUseCase:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, command) -> None:
        self.calls += 1
        raise RetryableExecutionError('Temporary failure')


@pytest.mark.asyncio
async def test_process_code_submission_propagates_retryable_error() -> None:
    process_use_case = RetryableProcessUseCase()
    submission_id = uuid4()

    with pytest.raises(RetryableExecutionError):
        await process_code_submission(
            submission_id=submission_id,
            process_use_case=process_use_case,
        )

    assert process_use_case.calls == 1
