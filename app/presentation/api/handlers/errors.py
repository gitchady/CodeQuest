from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.application.exceptions import (
    ApplicationError,
    AnswerOptionNotFoundError,
    CodeSubmissionNotFoundError,
    CodeTaskNotFoundError,
    CourseNotFoundError,
    LectureNotFoundError,
    ModuleNotFoundError,
    PermissionDeniedError as ApplicationPermissionDeniedError,
    QuestionAttemptNotFoundError,
    QuestionNotFoundError,
    SectionNotFoundError,
    TaskNotFoundError,
    TestCaseNotFoundError,
)
from app.domain.exceptions import DomainError
from app.presentation.api.schemas import ErrorResponse
from app.presentation.exceptions import (
    AuthenticationError,
    PermissionDeniedError as PresentationPermissionDeniedError,
)

ExceptionHandler = Callable[[Request, Exception], Response | Awaitable[Response]]


def build_error_response(error: str, message: str, status_code: int) -> JSONResponse:
    payload = ErrorResponse(error=error, message=message)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return build_error_response(
        error="domain_error",
        message=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return build_error_response(
        error="application_error",
        message=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def course_not_found_handler(request: Request, exc: CourseNotFoundError) -> JSONResponse:
    return build_error_response(
        error="course_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def module_not_found_handler(request: Request, exc: ModuleNotFoundError) -> JSONResponse:
    return build_error_response(
        error="module_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def section_not_found_handler(request: Request, exc: SectionNotFoundError) -> JSONResponse:
    return build_error_response(
        error="section_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def lecture_not_found_handler(request: Request, exc: LectureNotFoundError) -> JSONResponse:
    return build_error_response(
        error="lecture_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    return build_error_response(
        error="authentication_error",
        message=str(exc),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def application_permission_denied_handler(
    request: Request,
    exc: ApplicationPermissionDeniedError,
) -> JSONResponse:
    return build_error_response(
        error="permission_denied",
        message=str(exc),
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def presentation_permission_denied_handler(
    request: Request,
    exc: PresentationPermissionDeniedError,
) -> JSONResponse:
    return build_error_response(
        error="permission_denied",
        message=str(exc),
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def question_not_found_handler(request: Request, exc: QuestionNotFoundError) -> JSONResponse:
    return build_error_response(
        error="question_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def answer_option_not_found_handler(
    request: Request,
    exc: AnswerOptionNotFoundError,
) -> JSONResponse:
    return build_error_response(
        error="answer_option_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def question_attempt_not_found_handler(
    request: Request,
    exc: QuestionAttemptNotFoundError,
) -> JSONResponse:
    return build_error_response(
        error="question_attempt_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    return build_error_response(
        error='task_not_found',
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def code_task_not_found_handler(
    request: Request,
    exc: CodeTaskNotFoundError,
) -> JSONResponse:
    return build_error_response(
        error='code_task_not_found',
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def test_case_not_found_handler(
    request: Request,
    exc: TestCaseNotFoundError,
) -> JSONResponse:
    return build_error_response(
        error='test_case_not_found',
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def code_submission_not_found_handler(
    request: Request,
    exc: CodeSubmissionNotFoundError,
) -> JSONResponse:
    return build_error_response(
        error='code_submission_not_found',
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )

def register_exception_handlers(app: FastAPI) -> None:
    def add_handler(exc_class: type[Exception], handler: Callable[..., object]) -> None:
        app.add_exception_handler(exc_class, cast(ExceptionHandler, handler))

    add_handler(DomainError, domain_error_handler)
    add_handler(ApplicationError, application_error_handler)
    add_handler(AuthenticationError, authentication_error_handler)
    add_handler(
        ApplicationPermissionDeniedError,
        application_permission_denied_handler,
    )
    add_handler(
        PresentationPermissionDeniedError,
        presentation_permission_denied_handler,
    )
    add_handler(CourseNotFoundError, course_not_found_handler)
    add_handler(ModuleNotFoundError, module_not_found_handler)
    add_handler(SectionNotFoundError, section_not_found_handler)
    add_handler(LectureNotFoundError, lecture_not_found_handler)
    add_handler(QuestionNotFoundError, question_not_found_handler)
    add_handler(AnswerOptionNotFoundError, answer_option_not_found_handler)
    add_handler(QuestionAttemptNotFoundError, question_attempt_not_found_handler)
    add_handler(TaskNotFoundError, task_not_found_handler)
    add_handler(CodeTaskNotFoundError, code_task_not_found_handler)
    add_handler(TestCaseNotFoundError, test_case_not_found_handler)
    add_handler(CodeSubmissionNotFoundError, code_submission_not_found_handler)
