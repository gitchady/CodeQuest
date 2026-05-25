from app.application.use_cases.code_submissions.complete_code_submission import \
    CompleteCodeSubmissionUseCase
from app.application.use_cases.code_submissions.process_code_submission import \
    ProcessCodeSubmissionUseCase
from app.bootstrap.build_submission_queue import build_submission_queue
from app.domain.entities.code_task import CodeTaskLanguage
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.execution.docker_code_execution_gateway import \
    DockerCodeExecutionGateway
from app.infrastructure.execution.docker_runner import DockerRunConfig, DockerRunner
from app.infrastructure.execution.execution_profile_registry import (
    ExecutionProfile,
    ExecutionProfileRegistry,
)
from app.infrastructure.execution.java_submission_bundle_builder import JavaSubmissionBundleBuilder
from app.infrastructure.execution.python_submission_bundle_builder import \
    PythonSubmissionBundleBuilder
from app.infrastructure.workers.code_submission_worker import CodeSubmissionWorker
from app.infrastructure.database.database import SessionFactory


def build_code_submission_worker() -> CodeSubmissionWorker:
    queue = build_submission_queue()
    uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    runner = DockerRunner(
        config=DockerRunConfig(),
    )
    profile_registry = ExecutionProfileRegistry(
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
    )
    execution_gateway = DockerCodeExecutionGateway(
        runner=runner,
        profile_registry=profile_registry,
    )
    complete_use_case = CompleteCodeSubmissionUseCase(uow=uow)
    process_use_case = ProcessCodeSubmissionUseCase(
        uow=uow,
        execution_gateway=execution_gateway,
        complete_use_case=complete_use_case,
    )
    return CodeSubmissionWorker(
        queue=queue,
        process_use_case=process_use_case,
    )
