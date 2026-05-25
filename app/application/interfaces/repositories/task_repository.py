from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.task import Task


class TaskRepository(ABC):
    @abstractmethod
    async def add(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, task_ids: list[UUID]) -> list[Task]:
        raise NotImplementedError