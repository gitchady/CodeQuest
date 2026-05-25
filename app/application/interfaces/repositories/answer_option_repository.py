from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.answer_option import AnswerOption


class AnswerOptionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, answer_option_id: UUID) -> AnswerOption | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, answer_option_ids: list[UUID]) -> list[AnswerOption]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, answer_option: AnswerOption) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, answer_option: AnswerOption) -> None:
        raise NotImplementedError

    @abstractmethod
    async def remove(self, answer_option_id: UUID) -> None:
        raise NotImplementedError