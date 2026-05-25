from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import TaskNotFoundError
from app.application.interfaces.repositories.task_repository import TaskRepository
from app.domain.entities.task import Task


@dataclass(slots=True)
class GetTaskQuery:
    task_id: UUID


class GetTaskUseCase:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    async def execute(self, query: GetTaskQuery) -> Task:
        task = await self.task_repository.get_by_id(query.task_id)
        if task is None:
            raise TaskNotFoundError('Task not found.')
        return task