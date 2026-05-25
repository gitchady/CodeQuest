from abc import ABC, abstractmethod

from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.code_task import CodeTask
from app.domain.entities.execution_result import ExecutionResult
from app.domain.entities.test_case import TestCase


class CodeExecutionGateway(ABC):
    @abstractmethod
    async def execute(
            self,
            code_task: CodeTask,
            submission: CodeSubmission,
            test_cases: list[TestCase],
    ) -> ExecutionResult:
        raise NotImplementedError
