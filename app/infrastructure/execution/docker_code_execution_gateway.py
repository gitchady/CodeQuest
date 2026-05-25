import logging
from uuid import UUID

from app.application.interfaces.code_execution_gateway import CodeExecutionGateway
from app.domain.entities.code_submission import CodeSubmission
from app.domain.entities.code_task import CodeTask
from app.domain.entities.execution_result import ExecutionResult, ExecutionStatus
from app.domain.entities.test_case import TestCase
from app.infrastructure.execution.docker_runner import DockerRunResult, DockerRunner
from app.infrastructure.execution.execution_profile_registry import ExecutionProfileRegistry


logger = logging.getLogger(__name__)


class DockerCodeExecutionGateway(CodeExecutionGateway):
    def __init__(
        self,
        runner: DockerRunner,
        profile_registry: ExecutionProfileRegistry,
    ) -> None:
        self.runner = runner
        self.profile_registry = profile_registry

    async def execute(
        self,
        code_task: CodeTask,
        submission: CodeSubmission,
        test_cases: list[TestCase],
    ) -> ExecutionResult:
        profile = self.profile_registry.get(code_task.language)
        temp_dir, bundle = profile.bundle_builder.build(submission, test_cases)

        try:
            run_result = await self.runner.run(
                image=profile.image,
                bundle_dir=bundle.directory,
                command=bundle.command,
                time_limit_seconds=code_task.time_limit_seconds,
                memory_limit_mb=code_task.memory_limit_mb,
            )
        finally:
            temp_dir.cleanup()
        logger.debug(
            'Code submission executed',
            extra={
                'submission_id': str(submission.id),
                'exit_code': run_result.exit_code,
                'stdout': run_result.stdout,
                'stderr': run_result.stderr,
            },
        )
        return self._to_execution_result(
            submission_id=submission.id,
            run_result=run_result,
            total_test_cases=len(test_cases),
        )

    def _to_execution_result(
        self,
        submission_id: UUID,
        run_result: DockerRunResult,
        total_test_cases: int,
    ) -> ExecutionResult:
        if run_result.exit_code == 0:
            return ExecutionResult(
                submission_id=submission_id,
                status=ExecutionStatus.PASSED,
                passed_test_cases=total_test_cases,
                total_test_cases=total_test_cases,
                stdout=run_result.stdout,
                stderr=run_result.stderr,
                error_message='',
                exit_code=run_result.exit_code,
            )

        if run_result.exit_code is None:
            return ExecutionResult(
                submission_id=submission_id,
                status=ExecutionStatus.ERROR,
                passed_test_cases=0,
                total_test_cases=total_test_cases,
                stdout=run_result.stdout,
                stderr=run_result.stderr,
                error_message='Execution timed out.',
                exit_code=run_result.exit_code,
            )

        return ExecutionResult(
            submission_id=submission_id,
            status=ExecutionStatus.FAILED,
            passed_test_cases=0,
            total_test_cases=total_test_cases,
            stdout=run_result.stdout,
            stderr=run_result.stderr,
            error_message=run_result.stderr.strip(),
            exit_code=run_result.exit_code,
        )
