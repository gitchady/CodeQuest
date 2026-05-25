from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.progress import Progress


class ProgressRepository(ABC):
    @abstractmethod
    async def get_by_student_and_course(
        self,
        student_id: UUID,
        course_id: UUID,
    ) -> Progress | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, progress: Progress) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, progress: Progress) -> None:
        raise NotImplementedError