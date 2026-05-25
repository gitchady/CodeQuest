from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.application.use_cases.answer_options.create_answer_option import (
    CreateAnswerOptionCommand,
    CreateAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.delete_answer_option import (
    DeleteAnswerOptionCommand,
    DeleteAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.update_answer_option import (
    UpdateAnswerOptionCommand,
    UpdateAnswerOptionUseCase,
)
from app.application.use_cases.questions.create_question import (
    CreateQuestionCommand,
    CreateQuestionUseCase,
)
from app.application.use_cases.questions.delete_question import (
    DeleteQuestionCommand,
    DeleteQuestionUseCase,
)
from app.application.use_cases.questions.update_question import (
    UpdateQuestionCommand,
    UpdateQuestionUseCase,
)
from app.domain.entities.user import User
from app.presentation.api.dependencies import (
    get_create_answer_option_use_case,
    get_create_question_use_case,
    get_current_author_or_admin,
    get_delete_answer_option_use_case,
    get_delete_question_use_case,
    get_update_answer_option_use_case,
    get_update_question_use_case,
)
from app.presentation.api.schemas import (
    AnswerOptionResponse,
    CreateAnswerOptionRequest,
    CreateQuestionRequest,
    ErrorResponse,
    QuestionResponse,
    UpdateAnswerOptionRequest,
    UpdateQuestionRequest,
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
    '/sections/{section_id}/questions',
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create question',
    description='Creates a new interactive question inside the selected section.',
)
async def create_question(
    section_id: UUID,
    request: CreateQuestionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateQuestionUseCase = Depends(get_create_question_use_case),
) -> QuestionResponse:
    result = await use_case.execute(
        CreateQuestionCommand(
            actor=actor,
            section_id=section_id,
            text=request.text,
            position=request.position,
            question_type=request.question_type,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return QuestionResponse.model_validate(result)


@router.put(
    '/questions/{question_id}',
    response_model=QuestionResponse,
    summary='Update question',
    description='Updates an existing question if it can still be changed safely.',
)
async def update_question(
    question_id: UUID,
    request: UpdateQuestionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateQuestionUseCase = Depends(get_update_question_use_case),
) -> QuestionResponse:
    result = await use_case.execute(
        UpdateQuestionCommand(
            actor=actor,
            question_id=question_id,
            text=request.text,
            position=request.position,
            question_type=request.question_type,
            max_attempts=request.max_attempts,
            reward_points=request.reward_points,
        )
    )
    return QuestionResponse.model_validate(result)


@router.delete(
    '/questions/{question_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete question',
    description='Deletes a question if it has not been used in student attempts yet.',
)
async def delete_question(
    question_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteQuestionUseCase = Depends(get_delete_question_use_case),
) -> Response:
    await use_case.execute(
        DeleteQuestionCommand(
            actor=actor,
            question_id=question_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    '/questions/{question_id}/answer-options',
    response_model=AnswerOptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create answer option',
    description='Adds a new answer option to the selected question.',
)
async def create_answer_option(
    question_id: UUID,
    request: CreateAnswerOptionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: CreateAnswerOptionUseCase = Depends(get_create_answer_option_use_case),
) -> AnswerOptionResponse:
    result = await use_case.execute(
        CreateAnswerOptionCommand(
            actor=actor,
            question_id=question_id,
            text=request.text,
            position=request.position,
            is_correct=request.is_correct,
        )
    )
    return AnswerOptionResponse.model_validate(result)


@router.put(
    '/answer-options/{answer_option_id}',
    response_model=AnswerOptionResponse,
    summary='Update answer option',
    description='Updates an existing answer option if the question was not used yet.',
)
async def update_answer_option(
    answer_option_id: UUID,
    request: UpdateAnswerOptionRequest,
    actor: User = Depends(get_current_author_or_admin),
    use_case: UpdateAnswerOptionUseCase = Depends(get_update_answer_option_use_case),
) -> AnswerOptionResponse:
    result = await use_case.execute(
        UpdateAnswerOptionCommand(
            actor=actor,
            answer_option_id=answer_option_id,
            text=request.text,
            position=request.position,
            is_correct=request.is_correct,
        )
    )
    return AnswerOptionResponse.model_validate(result)


@router.delete(
    '/answer-options/{answer_option_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete answer option',
    description='Deletes an answer option if it keeps the question valid and unused.',
)
async def delete_answer_option(
    answer_option_id: UUID,
    actor: User = Depends(get_current_author_or_admin),
    use_case: DeleteAnswerOptionUseCase = Depends(get_delete_answer_option_use_case),
) -> Response:
    await use_case.execute(
        DeleteAnswerOptionCommand(
            actor=actor,
            answer_option_id=answer_option_id,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)