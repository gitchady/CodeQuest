from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import CodeTaskNotFoundError
from app.application.interfaces.repositories.code_task_repository import CodeTaskRepository
from app.domain.entities.code_task import CodeTask


@dataclass(slots=True)
class GetCodeTaskQuery:
    code_task_id: UUID


class GetCodeTaskUseCase:
    def __init__(self, code_task_repository: CodeTaskRepository) -> None:
        self.code_task_repository = code_task_repository

    async def execute(self, query: GetCodeTaskQuery) -> CodeTask:
        code_task = await self.code_task_repository.get_by_id(query.code_task_id)
        if code_task is None:
            raise CodeTaskNotFoundError('CodeTask not found.')
        return code_task