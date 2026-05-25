from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.use_cases.code_tasks.create_code_task import (
    CreateCodeTaskCommand,
    CreateCodeTaskUseCase,
)
from app.application.use_cases.code_tasks.update_code_task import (
    UpdateCodeTaskCommand,
    UpdateCodeTaskUseCase,
)
from app.application.use_cases.tasks.create_task import (
    CreateTaskCommand,
    CreateTaskUseCase,
)
from app.application.use_cases.tasks.update_task import (
    UpdateTaskCommand,
    UpdateTaskUseCase,
)
from app.application.use_cases.test_cases.create_test_case import (
    CreateTestCaseCommand,
    CreateTestCaseUseCase,
)
from app.application.use_cases.test_cases.update_test_case import (
    UpdateTestCaseCommand,
    UpdateTestCaseUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_create_code_task_use_case,
    get_create_task_use_case,
    get_create_test_case_use_case,
    get_current_author_or_admin,
    get_update_code_task_use_case,
    get_update_task_use_case,
    get_update_test_case_use_case,
)
from app.presentation.api.schemas import (
    CodeTaskResponse,
    CreateCodeTaskRequest,
    CreateTaskRequest,
    CreateTestCaseRequest,
    ErrorResponse,
    TaskResponse,
    TestCaseResponse,
    UpdateCodeTaskRequest,
    UpdateTaskRequest,
    UpdateTestCaseRequest,
)

router = APIRouter(
    prefix='/admin',
    tags=['Admin'],
    responses={
        401: {
            'description': 'Authentication credentials are missing or invalid.',
            'model': ErrorResponse,
        },
        403: {
            'description': 'Author or admin access is required.',
            'model': ErrorResponse,
        },
    },
)


@router.post(
    '/sections/{section_id}/tasks',
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create task',
)
async def create_task(
    section_id: UUID,
    request: CreateTaskRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        CreateTaskCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            statement=request.statement,
            position=request.position,
            check_type=request.check_type,
            expected_answer=request.expected_answer,
            accepted_answers=request.accepted_answers,
            answer_pattern=request.answer_pattern,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return TaskResponse.model_validate(result)


@router.put(
    '/tasks/{task_id}',
    response_model=TaskResponse,
    summary='Update task',
)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case),
) -> TaskResponse:
    result = await use_case.execute(
        UpdateTaskCommand(
            actor=actor,
            task_id=task_id,
            title=request.title,
            statement=request.statement,
            position=request.position,
            check_type=request.check_type,
            expected_answer=request.expected_answer,
            accepted_answers=request.accepted_answers,
            answer_pattern=request.answer_pattern,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return TaskResponse.model_validate(result)


@router.post(
    '/sections/{section_id}/code-tasks',
    response_model=CodeTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create code task',
)
async def create_code_task(
    section_id: UUID,
    request: CreateCodeTaskRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateCodeTaskUseCase = Depends(get_create_code_task_use_case),
) -> CodeTaskResponse:
    result = await use_case.execute(
        CreateCodeTaskCommand(
            actor=actor,
            section_id=section_id,
            title=request.title,
            statement=request.statement,
            position=request.position,
            language=request.language,
            starter_code=request.starter_code,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
            time_limit_seconds=request.time_limit_seconds,
            memory_limit_mb=request.memory_limit_mb,
        )
    )
    return CodeTaskResponse.model_validate(result)


@router.put(
    '/code-tasks/{code_task_id}',
    response_model=CodeTaskResponse,
    summary='Update code task',
)
async def update_code_task(
    code_task_id: UUID,
    request: UpdateCodeTaskRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateCodeTaskUseCase = Depends(get_update_code_task_use_case),
) -> CodeTaskResponse:
    result = await use_case.execute(
        UpdateCodeTaskCommand(
            actor=actor,
            code_task_id=code_task_id,
            title=request.title,
            statement=request.statement,
            position=request.position,
            language=request.language,
            starter_code=request.starter_code,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
            time_limit_seconds=request.time_limit_seconds,
            memory_limit_mb=request.memory_limit_mb,
        )
    )
    return CodeTaskResponse.model_validate(result)


@router.post(
    '/code-tasks/{code_task_id}/test-cases',
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create test case',
)
async def create_test_case(
    code_task_id: UUID,
    request: CreateTestCaseRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateTestCaseUseCase = Depends(get_create_test_case_use_case),
) -> TestCaseResponse:
    result = await use_case.execute(
        CreateTestCaseCommand(
            actor=actor,
            code_task_id=code_task_id,
            position=request.position,
            input_data=request.input_data,
            expected_output=request.expected_output,
            is_hidden=request.is_hidden,
            explanation=request.explanation,
        )
    )
    return TestCaseResponse.model_validate(result)


@router.put(
    '/test-cases/{test_case_id}',
    response_model=TestCaseResponse,
    summary='Update test case',
)
async def update_test_case(
    test_case_id: UUID,
    request: UpdateTestCaseRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateTestCaseUseCase = Depends(get_update_test_case_use_case),
) -> TestCaseResponse:
    result = await use_case.execute(
        UpdateTestCaseCommand(
            actor=actor,
            test_case_id=test_case_id,
            position=request.position,
            input_data=request.input_data,
            expected_output=request.expected_output,
            is_hidden=request.is_hidden,
            explanation=request.explanation,
        )
    )
    return TestCaseResponse.model_validate(result)