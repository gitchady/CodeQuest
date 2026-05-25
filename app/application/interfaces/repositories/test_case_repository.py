from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.test_case import TestCase


class TestCaseRepository(ABC):
    @abstractmethod
    async def add(self, test_case: TestCase) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, test_case_id: UUID) -> TestCase | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, test_case: TestCase) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_code_task_id(self, code_task_id: UUID) -> list[TestCase]:
        raise NotImplementedError