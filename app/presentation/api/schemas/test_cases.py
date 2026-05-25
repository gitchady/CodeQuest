from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestCaseWriteRequest(BaseModel):
    position: int = Field(ge=1)
    input_data: str
    expected_output: str
    is_hidden: bool = True
    explanation: str = ''


class CreateTestCaseRequest(TestCaseWriteRequest):
    pass


class UpdateTestCaseRequest(TestCaseWriteRequest):
    pass


class TestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code_task_id: UUID
    position: int
    input_data: str
    expected_output: str
    is_hidden: bool
    explanation: str