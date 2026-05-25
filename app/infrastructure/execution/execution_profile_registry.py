from dataclasses import dataclass

from app.domain.entities.code_task import CodeTaskLanguage
from app.infrastructure.execution.submission_bundle_builder import SubmissionBundleBuilder


@dataclass(slots=True, frozen=True)
class ExecutionProfile:
    image: str
    bundle_builder: SubmissionBundleBuilder


class ExecutionProfileRegistry:
    def __init__(
        self,
        profiles: dict[CodeTaskLanguage, ExecutionProfile],
    ) -> None:
        self.profiles = profiles

    def get(self, language: CodeTaskLanguage) -> ExecutionProfile:
        try:
            return self.profiles[language]
        except KeyError as exc:
            raise ValueError(f'Unsupported language: {language}') from exc