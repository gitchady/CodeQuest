import subprocess

import pytest
from sqlalchemy import select

from app.application.use_cases.code_submissions.complete_code_submission import \
    CompleteCodeSubmissionUseCase
from app.application.use_cases.code_submissions.process_code_submission import (
    ProcessCodeSubmissionCommand,
    ProcessCodeSubmissionUseCase,
)
from app.domain.entities.code_task import CodeTaskLanguage
from app.infrastructure.database.models import CodeSubmissionModel
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.execution.docker_code_execution_gateway import DockerCodeExecutionGateway
from app.infrastructure.execution.docker_runner import DockerRunConfig, DockerRunner
from app.infrastructure.execution.execution_profile_registry import ExecutionProfile, \
    ExecutionProfileRegistry
from app.infrastructure.execution.java_submission_bundle_builder import JavaSubmissionBundleBuilder
from app.infrastructure.execution.python_submission_bundle_builder import \
    PythonSubmissionBundleBuilder
import app.presentation.api.dependencies as api_dependencies


def docker_is_available() -> bool:
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


class FakeSubmissionQueue:
    def __init__(self) -> None:
        self.items = []

    async def enqueue(self, submission_id) -> None:
        self.items.append(submission_id)


@pytest.fixture
def fake_submission_queue(monkeypatch):
    queue = FakeSubmissionQueue()
    monkeypatch.setattr(
        api_dependencies,
        'build_submission_queue',
        lambda: queue,
    )
    return queue


@pytest.mark.asyncio
async def test_python_code_submission_flow(
        client,
        author_auth_headers,
        student_auth_headers,
        session_factory,
        fake_submission_queue,
):
    if not docker_is_available():
        pytest.skip('Docker daemon is not available.')

    course_response = await client.post(
        '/api/admin/courses',
        headers=author_auth_headers,
        json={'title': 'Code course', 'description': 'Course with code tasks.'},
    )
    course_id = course_response.json()['id']

    module_response = await client.post(
        f'/api/admin/courses/{course_id}/modules',
        headers=author_auth_headers,
        json={'title': 'Python', 'description': 'Practice', 'position': 1},
    )
    module_id = module_response.json()['id']

    section_response = await client.post(
        f'/api/admin/modules/{module_id}/sections',
        headers=author_auth_headers,
        json={'title': 'Basics', 'description': 'Intro', 'position': 1},
    )
    section_id = section_response.json()['id']

    code_task_response = await client.post(
        f'/api/admin/sections/{section_id}/code-tasks',
        headers=author_auth_headers,
        json={
            'title': 'Sum numbers',
            'statement': 'Read two integers and print their sum.',
            'position': 1,
            'language': 'python',
            'starter_code': 'a, b = map(int, input().split())',
            'max_attempts': 2,
            'reward_points': 5,
            'time_limit_seconds': 20,
            'memory_limit_mb': 128,
        },
    )
    code_task_id = code_task_response.json()['id']

    await client.post(
        f'/api/admin/code-tasks/{code_task_id}/test-cases',
        headers=author_auth_headers,
        json={
            'position': 1,
            'input_data': '2 3',
            'expected_output': '5',
            'is_hidden': False,
            'explanation': 'basic case',
        },
    )

    submission_response = await client.post(
        f'/api/learning/code-tasks/{code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'a, b = map(int, input().split())\nprint(a + b)'},
    )
    submission_id = submission_response.json()['id']

    uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
    runner = DockerRunner(config=DockerRunConfig())
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

    await process_use_case.execute(
        ProcessCodeSubmissionCommand(submission_id=submission_id)
    )

    async with session_factory() as session:
        submissions = (await session.execute(select(CodeSubmissionModel))).scalars().all()

    assert len(submissions) == 1
    assert submissions[0].status == 'passed'
