import asyncio
from uuid import UUID

from app.application.interfaces.submission_queue import SubmissionQueue


class InMemorySubmissionQueue(SubmissionQueue):
    def __init__(self) -> None:
        self._queue: asyncio.Queue[UUID] = asyncio.Queue()

    async def enqueue(self, submission_id: UUID) -> None:
        await self._queue.put(submission_id)

    async def dequeue(self) -> UUID:
        return await self._queue.get()
