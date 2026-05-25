from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.code_task import CodeTask


class CodeTaskRepository(ABC):
    @abstractmethod
    async def add(self, code_task: CodeTask) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, code_task_id: UUID) -> CodeTask | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, code_task: CodeTask) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, code_task_ids: list[UUID]) -> list[CodeTask]:
        raise NotImplementedError