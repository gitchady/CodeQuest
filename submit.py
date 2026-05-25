import argparse
import asyncio
from uuid import UUID

from app.application.use_cases.code_submissions.complete_code_submission import (
    CompleteCodeSubmissionUseCase,
)
from app.application.use_cases.code_submissions.process_code_submission import (
    ProcessCodeSubmissionCommand,
    ProcessCodeSubmissionUseCase,
)
from app.domain.entities.code_task import CodeTaskLanguage
from app.infrastructure.database.database import SessionFactory
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.execution.docker_code_execution_gateway import (
    DockerCodeExecutionGateway,
)
from app.infrastructure.execution.docker_runner import DockerRunConfig, DockerRunner
from app.infrastructure.execution.execution_profile_registry import (
    ExecutionProfile,
    ExecutionProfileRegistry,
)
from app.infrastructure.execution.java_submission_bundle_builder import (
    JavaSubmissionBundleBuilder,
)
from app.infrastructure.execution.python_submission_bundle_builder import (
    PythonSubmissionBundleBuilder,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Process one code submission.')
    parser.add_argument('submission_id', type=UUID)
    return parser.parse_args()


def build_process_use_case() -> ProcessCodeSubmissionUseCase:
    uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    execution_gateway = DockerCodeExecutionGateway(
        runner=DockerRunner(config=DockerRunConfig()),
        profile_registry=ExecutionProfileRegistry(
            profiles={
                CodeTaskLanguage.PYTHON: ExecutionProfile(
                    image='python:3.12-alpine',
                    bundle_builder=PythonSubmissionBundleBuilder(),
                ),
                CodeTaskLanguage.JAVA: ExecutionProfile(
                    image='eclipse-temurin:21-jdk-jammy',
                    bundle_builder=JavaSubmissionBundleBuilder(),
                ),
            }
        ),
    )
    complete_use_case = CompleteCodeSubmissionUseCase(uow=uow)
    return ProcessCodeSubmissionUseCase(
        uow=uow,
        execution_gateway=execution_gateway,
        complete_use_case=complete_use_case,
    )


async def main() -> None:
    args = parse_args()
    process_use_case = build_process_use_case()
    await process_use_case.execute(
        ProcessCodeSubmissionCommand(submission_id=args.submission_id)
    )


if __name__ == '__main__':
    asyncio.run(main())
