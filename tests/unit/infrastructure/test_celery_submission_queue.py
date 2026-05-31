from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.infrastructure.queues.celery_submission_queue import CelerySubmissionQueue


class RecordingTask:
    def __init__(self) -> None:
        self.delay_calls: list[str] = []

    def delay(self, submission_id: str) -> SimpleNamespace:
        self.delay_calls.append(submission_id)
        return SimpleNamespace(id='celery-task-id')


@pytest.mark.asyncio
async def test_celery_submission_queue_dispatches_submission_id_as_string() -> None:
    task = RecordingTask()
    queue = CelerySubmissionQueue(task=task)
    submission_id = uuid4()

    await queue.enqueue(submission_id)

    assert task.delay_calls == [str(submission_id)]
