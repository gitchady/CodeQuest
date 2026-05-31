from typing import Protocol
from uuid import UUID

from app.application.interfaces.submission_queue import SubmissionQueue


class CeleryTask(Protocol):
    def delay(self, submission_id: str) -> object:
        raise NotImplementedError


class CelerySubmissionQueue(SubmissionQueue):
    def __init__(self, task: CeleryTask) -> None:
        self.task = task

    async def enqueue(self, submission_id: UUID) -> None:
        self.task.delay(str(submission_id))
