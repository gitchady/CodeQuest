from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.question_attempt import QuestionAttempt


class QuestionAttemptRepository(ABC):
    @abstractmethod
    async def get_by_id(self, attempt_id: UUID) -> QuestionAttempt | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_student_and_question(
        self,
        student_id: UUID,
        question_id: UUID,
    ) -> list[QuestionAttempt]:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_question_id(self, question_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def add(self, attempt: QuestionAttempt) -> None:
        raise NotImplementedError