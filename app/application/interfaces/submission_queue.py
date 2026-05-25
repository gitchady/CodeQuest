from abc import ABC, abstractmethod
from uuid import UUID


class SubmissionQueue(ABC):
    @abstractmethod
    async def enqueue(self, submission_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def dequeue(self) -> UUID:
        raise NotImplementedError