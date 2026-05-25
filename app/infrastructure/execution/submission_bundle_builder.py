from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.test_case import TestCase


@dataclass(slots=True)
class ExecutionBundle:
    directory: Path
    command: list[str]


class SubmissionBundleBuilder(ABC):
    @abstractmethod
    def build(
        self,
        submission: CodeSubmission,
        test_cases: list[TestCase],
    ) -> tuple[TemporaryDirectory[str], ExecutionBundle]:
        raise NotImplementedError