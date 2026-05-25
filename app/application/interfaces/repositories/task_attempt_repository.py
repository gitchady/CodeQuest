from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.task_attempt import TaskAttempt


class TaskAttemptRepository(ABC):
    @abstractmethod
    async def add(self, attempt: TaskAttempt) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, attempt_id: UUID) -> TaskAttempt | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_task_id(self, task_id: UUID) -> list[TaskAttempt]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_student_and_task(
            self,
            student_id: UUID,
            task_id: UUID,
    ) -> list[TaskAttempt]:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_task_id(self, task_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def update(self, attempt: TaskAttempt) -> None:
        raise NotImplementedError
