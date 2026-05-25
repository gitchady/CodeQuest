from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.test_case_repository import TestCaseRepository
from app.domain.entities.test_case import TestCase
from app.infrastructure.database.mappers.test_case_mapper import TestCaseMapper
from app.infrastructure.database.models.test_case_model import TestCaseModel


class SqlAlchemyTestCaseRepository(TestCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, test_case: TestCase) -> None:
        self.session.add(TestCaseMapper.to_model(test_case))
        await self.session.flush()

    async def get_by_id(self, test_case_id: UUID) -> TestCase | None:
        model = await self.session.get(TestCaseModel, str(test_case_id))
        return None if model is None else TestCaseMapper.to_domain(model)

    async def update(self, test_case: TestCase) -> None:
        model = await self.session.get(TestCaseModel, str(test_case.id))
        if model is None:
            return

        model.position = test_case.position
        model.input_data = test_case.input_data
        model.expected_output = test_case.expected_output
        model.is_hidden = test_case.is_hidden
        model.explanation = test_case.explanation
        await self.session.flush()

    async def list_by_code_task_id(self, code_task_id: UUID) -> list[TestCase]:
        stmt = select(TestCaseModel).where(TestCaseModel.code_task_id == str(code_task_id))
        result = await self.session.execute(stmt)
        return [TestCaseMapper.to_domain(model) for model in result.scalars().all()]