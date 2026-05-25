from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import InvalidTestCaseError


@dataclass(slots=True)
class TestCase:
    id: UUID
    code_task_id: UUID
    position: int
    input_data: str
    expected_output: str
    is_hidden: bool = True
    explanation: str = ''

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.position < 1:
            raise InvalidTestCaseError('TestCase position must be positive.')
        if self.input_data is None:
            raise InvalidTestCaseError('TestCase input_data cannot be None.')
        if self.expected_output is None:
            raise InvalidTestCaseError('TestCase expected_output cannot be None.')

    def update(
        self,
        input_data: str,
        expected_output: str,
        is_hidden: bool,
        explanation: str,
        position: int,
    ) -> None:
        self.input_data = input_data
        self.expected_output = expected_output
        self.is_hidden = is_hidden
        self.explanation = explanation
        self.position = position
        self._validate()
