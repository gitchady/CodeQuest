from collections.abc import AsyncIterator

from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from app.domain.entities.user import User

from app.presentation.exceptions import AuthenticationError
from app.presentation.exceptions import PermissionDeniedError

from app.infrastructure.database import SessionFactory, SqlAlchemyUnitOfWork
from app.infrastructure.security.jwt_token_service import InvalidTokenError

from app.application.use_cases.courses.create_course import CreateCourseUseCase
from app.application.use_cases.courses.delete_course import DeleteCourseUseCase
from app.application.use_cases.courses.get_course import GetCourseUseCase
from app.application.use_cases.courses.get_course_structure import GetCourseStructureUseCase
from app.application.use_cases.courses.get_courses import GetCoursesUseCase
from app.application.use_cases.courses.update_course import UpdateCourseUseCase
from app.application.use_cases.lectures.create_lecture import CreateLectureUseCase
from app.application.use_cases.lectures.delete_lecture import DeleteLectureUseCase
from app.application.use_cases.lectures.get_lecture import GetLectureUseCase
from app.application.use_cases.lectures.update_lecture import UpdateLectureUseCase
from app.application.use_cases.modules.create_module import CreateModuleUseCase
from app.application.use_cases.modules.delete_module import DeleteModuleUseCase
from app.application.use_cases.modules.update_module import UpdateModuleUseCase
from app.application.use_cases.sections.create_section import CreateSectionUseCase
from app.application.use_cases.sections.delete_section import DeleteSectionUseCase
from app.application.use_cases.sections.update_section import UpdateSectionUseCase
from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.interfaces.services.token_service import TokenService
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.application.use_cases.answer_options.create_answer_option import (
    CreateAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.delete_answer_option import (
    DeleteAnswerOptionUseCase,
)
from app.application.use_cases.answer_options.update_answer_option import (
    UpdateAnswerOptionUseCase,
)
from app.application.use_cases.questions.create_question import CreateQuestionUseCase
from app.application.use_cases.questions.delete_question import DeleteQuestionUseCase
from app.application.use_cases.questions.update_question import UpdateQuestionUseCase


from app.application.use_cases.question_attempts.get_question_attempt_result import (
    GetQuestionAttemptResultUseCase,
)
from app.application.use_cases.question_attempts.start_question_attempt import (
    StartQuestionAttemptUseCase,
)
from app.application.use_cases.question_attempts.submit_question_answer import (
    SubmitQuestionAnswerUseCase,
)
from app.application.use_cases.tasks.create_task import CreateTaskUseCase
from app.application.use_cases.tasks.update_task import UpdateTaskUseCase
from app.application.use_cases.code_tasks.create_code_task import CreateCodeTaskUseCase
from app.application.use_cases.code_tasks.get_code_task import GetCodeTaskUseCase
from app.application.use_cases.code_submissions.get_code_submission import (
    GetCodeSubmissionUseCase,
)
from app.application.use_cases.code_submissions.list_code_submissions import (
    ListCodeSubmissionsUseCase,
)
from app.application.use_cases.code_submissions.submit_code_submission import (
    SubmitCodeSubmissionUseCase,
)
from app.application.use_cases.code_tasks.update_code_task import UpdateCodeTaskUseCase
from app.application.use_cases.questions.get_question import GetQuestionUseCase
from app.application.use_cases.tasks.get_task import GetTaskUseCase
from app.application.use_cases.task_attempts.submit_task_answer import (
    SubmitTaskAnswerUseCase,
)
from app.application.use_cases.test_cases.create_test_case import CreateTestCaseUseCase
from app.application.use_cases.test_cases.update_test_case import UpdateTestCaseUseCase
from app.bootstrap.build_submission_queue import build_submission_queue


http_bearer = HTTPBearer(auto_error=False)


async def get_uow() -> AsyncIterator[SqlAlchemyUnitOfWork]:
    async with SqlAlchemyUnitOfWork(session_factory=SessionFactory) as uow:
        yield uow


def get_get_courses_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetCoursesUseCase:
    return GetCoursesUseCase(course_repository=uow.courses)


def get_get_course_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetCourseUseCase:
    return GetCourseUseCase(course_repository=uow.courses)


def get_get_course_structure_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetCourseStructureUseCase:
    return GetCourseStructureUseCase(
        course_repository=uow.courses,
        module_repository=uow.modules,
        section_repository=uow.sections,
        lecture_repository=uow.lectures,
        task_repository=uow.tasks,
        code_task_repository=uow.code_tasks,
    )


def get_get_lecture_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetLectureUseCase:
    return GetLectureUseCase(lecture_repository=uow.lectures)


def get_create_course_use_case() -> CreateCourseUseCase:
    return CreateCourseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_course_use_case() -> UpdateCourseUseCase:
    return UpdateCourseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_course_use_case() -> DeleteCourseUseCase:
    return DeleteCourseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_module_use_case() -> CreateModuleUseCase:
    return CreateModuleUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_module_use_case() -> UpdateModuleUseCase:
    return UpdateModuleUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_module_use_case() -> DeleteModuleUseCase:
    return DeleteModuleUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_section_use_case() -> CreateSectionUseCase:
    return CreateSectionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_section_use_case() -> UpdateSectionUseCase:
    return UpdateSectionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_section_use_case() -> DeleteSectionUseCase:
    return DeleteSectionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_lecture_use_case() -> CreateLectureUseCase:
    return CreateLectureUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_lecture_use_case() -> UpdateLectureUseCase:
    return UpdateLectureUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_lecture_use_case() -> DeleteLectureUseCase:
    return DeleteLectureUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_password_hasher() -> PasswordHasher:
    return PwdlibPasswordHasher()


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        password_hasher=get_password_hasher(),
    )


def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def get_token_service() -> TokenService:
    return JwtTokenService()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
        token_service: TokenService = Depends(get_token_service),
) -> User:
    if credentials is None:
        raise AuthenticationError('Authentication credentials were not provided.')

    if credentials.scheme.lower() != 'bearer':
        raise AuthenticationError('Authentication scheme must be Bearer.')

    try:
        user_id = token_service.get_user_id(credentials.credentials)
    except InvalidTokenError as exc:
        raise AuthenticationError(str(exc)) from exc

    user = await uow.users.get_by_id(user_id)
    if user is None:
        raise AuthenticationError('User from token was not found.')

    return user


async def get_current_admin(
        current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.can_manage_platform():
        raise PermissionDeniedError('Admin access is required.')
    return current_user


async def get_current_author_or_admin(
        current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.can_manage_content():
        raise PermissionDeniedError('Author or admin access is required.')
    return current_user


def get_create_question_use_case() -> CreateQuestionUseCase:
    return CreateQuestionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_question_use_case() -> UpdateQuestionUseCase:
    return UpdateQuestionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_question_use_case() -> DeleteQuestionUseCase:
    return DeleteQuestionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_answer_option_use_case() -> CreateAnswerOptionUseCase:
    return CreateAnswerOptionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_answer_option_use_case() -> UpdateAnswerOptionUseCase:
    return UpdateAnswerOptionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_delete_answer_option_use_case() -> DeleteAnswerOptionUseCase:
    return DeleteAnswerOptionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_start_question_attempt_use_case() -> StartQuestionAttemptUseCase:
    return StartQuestionAttemptUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_submit_question_answer_use_case() -> SubmitQuestionAnswerUseCase:
    return SubmitQuestionAnswerUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_get_question_attempt_result_use_case() -> GetQuestionAttemptResultUseCase:
    return GetQuestionAttemptResultUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_task_use_case() -> CreateTaskUseCase:
    return CreateTaskUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_task_use_case() -> UpdateTaskUseCase:
    return UpdateTaskUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_code_task_use_case() -> CreateCodeTaskUseCase:
    return CreateCodeTaskUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_code_task_use_case() -> UpdateCodeTaskUseCase:
    return UpdateCodeTaskUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_create_test_case_use_case() -> CreateTestCaseUseCase:
    return CreateTestCaseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_update_test_case_use_case() -> UpdateTestCaseUseCase:
    return UpdateTestCaseUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_submit_task_answer_use_case() -> SubmitTaskAnswerUseCase:
    return SubmitTaskAnswerUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_submit_code_submission_use_case() -> SubmitCodeSubmissionUseCase:
    return SubmitCodeSubmissionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory),
        submission_queue=build_submission_queue(),
    )

def get_get_code_submission_use_case() -> GetCodeSubmissionUseCase:
    return GetCodeSubmissionUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )


def get_list_code_submissions_use_case() -> ListCodeSubmissionsUseCase:
    return ListCodeSubmissionsUseCase(
        uow=SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    )

def get_get_question_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetQuestionUseCase:
    return GetQuestionUseCase(
        question_repository=uow.questions,
        answer_option_repository=uow.answer_options,
    )


def get_get_task_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetTaskUseCase:
    return GetTaskUseCase(task_repository=uow.tasks)


def get_get_code_task_use_case(
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetCodeTaskUseCase:
    return GetCodeTaskUseCase(code_task_repository=uow.code_tasks)




