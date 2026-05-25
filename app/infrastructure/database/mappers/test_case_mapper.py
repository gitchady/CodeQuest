from uuid import UUID

from app.domain.entities.test_case import TestCase
from app.infrastructure.database.models.test_case_model import TestCaseModel


class TestCaseMapper:
    @staticmethod
    def to_domain(model: TestCaseModel) -> TestCase:
        return TestCase(
            id=UUID(model.id),
            code_task_id=UUID(model.code_task_id),
            position=model.position,
            input_data=model.input_data,
            expected_output=model.expected_output,
            is_hidden=model.is_hidden,
            explanation=model.explanation,
        )

    @staticmethod
    def to_model(entity: TestCase) -> TestCaseModel:
        return TestCaseModel(
            id=str(entity.id),
            code_task_id=str(entity.code_task_id),
            position=entity.position,
            input_data=entity.input_data,
            expected_output=entity.expected_output,
            is_hidden=entity.is_hidden,
            explanation=entity.explanation,
        )