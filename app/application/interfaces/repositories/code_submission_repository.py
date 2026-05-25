from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.code_submission import CodeSubmission


class CodeSubmissionRepository(ABC):
    @abstractmethod
    async def add(self, submission: CodeSubmission) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> CodeSubmission | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, submission: CodeSubmission) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_code_task_id(self, code_task_id: UUID) -> list[CodeSubmission]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_code_task_and_student_id(
        self,
        code_task_id: UUID,
        student_id: UUID,
    ) -> list[CodeSubmission]:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_code_task_id(self, code_task_id: UUID) -> bool:
        raise NotImplementedError
