from uuid import uuid4

import pytest

from app.application.exceptions import RetryableExecutionError
from app.infrastructure.workers.code_submission_worker import CodeSubmissionWorker


class FakeSubmissionQueue:
    def __init__(self) -> None:
        self.items = []
        self.enqueued_submission_ids = []

    async def enqueue(self, submission_id):
        self.items.append(submission_id)
        self.enqueued_submission_ids.append(submission_id)

    async def dequeue(self):
        if not self.items:
            raise AssertionError('Queue is empty in test.')
        return self.items.pop(0)


class BrokenSubmissionQueue(FakeSubmissionQueue):
    async def dequeue(self):
        raise RuntimeError('Redis is unavailable')


class FakeProcessUseCase:
    def __init__(self) -> None:
        self.received_submission_ids = []

    async def execute(self, command) -> None:
        self.received_submission_ids.append(command.submission_id)





@pytest.mark.asyncio
async def test_worker_processes_submission_from_queue() -> None:
    queue = FakeSubmissionQueue()
    process_use_case = FakeProcessUseCase()
    worker = CodeSubmissionWorker(queue=queue, process_use_case=process_use_case)

    submission_id = uuid4()
    await queue.enqueue(submission_id)

    await worker.run_once()

    assert process_use_case.received_submission_ids == [submission_id]


class RetryableProcessUseCase:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, command) -> None:
        self.calls += 1
        raise RetryableExecutionError('Temporary failure')


@pytest.mark.asyncio
async def test_worker_requeues_submission_on_retryable_error() -> None:
    queue = FakeSubmissionQueue()
    process_use_case = RetryableProcessUseCase()
    worker = CodeSubmissionWorker(queue=queue, process_use_case=process_use_case)

    submission_id = uuid4()
    await queue.enqueue(submission_id)

    await worker.run_once()

    assert queue.enqueued_submission_ids.count(submission_id) >= 2


@pytest.mark.asyncio
async def test_worker_does_not_crash_when_dequeue_fails() -> None:
    queue = BrokenSubmissionQueue()
    process_use_case = FakeProcessUseCase()
    worker = CodeSubmissionWorker(queue=queue, process_use_case=process_use_case)

    await worker.run_once()

    assert process_use_case.received_submission_ids == []
