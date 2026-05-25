from app.presentation.api.schemas.auth import RegisterUserRequest, RegisteredUserResponse, \
    LoginRequest, TokenResponse, CurrentUserResponse
from app.presentation.api.schemas.content import (
    CourseListItemResponse,
    CourseResponse,
    CourseStructureResponse,
    LectureResponse,
    LectureStructureResponse,
    ModuleStructureResponse,
    SectionStructureResponse, TaskStructureResponse, CodeTaskStructureResponse,
    CodeTaskDetailsResponse, QuestionDetailsResponse, TaskDetailsResponse,
)
from app.presentation.api.schemas.courses import CreateCourseRequest, UpdateCourseRequest
from app.presentation.api.schemas.errors import ErrorResponse
from app.presentation.api.schemas.lectures import CreateLectureRequest, UpdateLectureRequest
from app.presentation.api.schemas.modules import (
    CreateModuleRequest,
    ModuleResponse,
    UpdateModuleRequest,
)
from app.presentation.api.schemas.sections import (
    CreateSectionRequest,
    SectionResponse,
    UpdateSectionRequest,
)

from app.presentation.api.schemas.questions import (
    AnswerOptionResponse,
    CreateAnswerOptionRequest,
    CreateQuestionRequest,
    QuestionResponse,
    UpdateAnswerOptionRequest,
    UpdateQuestionRequest,
)

from app.presentation.api.schemas.question_attempts import (
    QuestionAttemptResultResponse,
    StartQuestionAttemptResponse,
    SubmitQuestionAnswerRequest,
)

from app.presentation.api.schemas.tasks import (
    CreateTaskRequest,
    TaskResponse,
    UpdateTaskRequest,
)
from app.presentation.api.schemas.code_tasks import (
    CodeTaskResponse,
    CreateCodeTaskRequest,
    UpdateCodeTaskRequest,
)
from app.presentation.api.schemas.test_cases import (
    CreateTestCaseRequest,
    TestCaseResponse,
    UpdateTestCaseRequest,
)

from app.presentation.api.schemas.task_attempts import (
    SubmitTaskAnswerRequest,
    TaskAttemptResponse,
)
from app.presentation.api.schemas.code_submissions import (
    CodeSubmissionResponse,
    SubmitCodeSubmissionRequest,
)

__all__ = [
    "CourseListItemResponse",
    "CourseResponse",
    "CourseStructureResponse",
    "LectureResponse",
    "LectureStructureResponse",
    "ModuleStructureResponse",
    "SectionStructureResponse",
    "CreateCourseRequest",
    "UpdateCourseRequest",
    "CreateModuleRequest",
    "UpdateModuleRequest",
    "ModuleResponse",
    "CreateSectionRequest",
    "UpdateSectionRequest",
    "SectionResponse",
    "CreateLectureRequest",
    "UpdateLectureRequest",
    "ErrorResponse",
    "RegisterUserRequest",
    "RegisteredUserResponse",
    "LoginRequest",
    "TokenResponse",
    "CurrentUserResponse",
    'CreateQuestionRequest',
    'UpdateQuestionRequest',
    'QuestionResponse',
    'CreateAnswerOptionRequest',
    'UpdateAnswerOptionRequest',
    'AnswerOptionResponse',
    'StartQuestionAttemptResponse',
    'SubmitQuestionAnswerRequest',
    'QuestionAttemptResultResponse',
    'CreateTaskRequest',
    'CreateTestCaseRequest',
    'TaskResponse',
    'UpdateTaskRequest',
    'CodeTaskResponse',
    'CreateCodeTaskRequest',
    'UpdateCodeTaskRequest',
    'CreateTestCaseRequest',
    'TestCaseResponse',
    'UpdateTestCaseRequest',
    'SubmitTaskAnswerRequest',
    'TaskAttemptResponse',
    'CodeSubmissionResponse',
    'SubmitCodeSubmissionRequest',
    'TaskStructureResponse',
    'CodeTaskStructureResponse',
    "CodeTaskDetailsResponse",
    "QuestionDetailsResponse",
    "TaskDetailsResponse",
]
