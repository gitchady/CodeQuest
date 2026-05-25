from app.infrastructure.database.repositories.answer_option_repository import \
    SqlAlchemyAnswerOptionRepository
from app.infrastructure.database.repositories.course_repository import (
    SqlAlchemyCourseRepository,
)
from app.infrastructure.database.repositories.lecture_repository import (
    SqlAlchemyLectureRepository,
)
from app.infrastructure.database.repositories.module_repository import (
    SqlAlchemyModuleRepository,
)
from app.infrastructure.database.repositories.progress_repository import \
    SqlAlchemyProgressRepository

from app.infrastructure.database.repositories.question_attempt_repository import \
    SqlAlchemyQuestionAttemptRepository

from app.infrastructure.database.repositories.question_repository import \
    SqlAlchemyQuestionRepository

from app.infrastructure.database.repositories.section_repository import (
    SqlAlchemySectionRepository,
)
from app.infrastructure.database.repositories.task_attempt_repository import \
    SqlAlchemyTaskAttemptRepository
from app.infrastructure.database.repositories.task_repository import SqlAlchemyTaskRepository

from app.infrastructure.database.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from app.infrastructure.database.repositories.code_submission_repository import (
    SqlAlchemyCodeSubmissionRepository,
)
from app.infrastructure.database.repositories.code_task_repository import (
    SqlAlchemyCodeTaskRepository,
)
from app.infrastructure.database.repositories.test_case_repository import (
    SqlAlchemyTestCaseRepository,
)

__all__ = [
    "SqlAlchemyCourseRepository",
    "SqlAlchemyModuleRepository",
    "SqlAlchemySectionRepository",
    "SqlAlchemyLectureRepository",
    "SqlAlchemyUserRepository",
    "SqlAlchemyQuestionRepository",
    "SqlAlchemyAnswerOptionRepository",
    "SqlAlchemyQuestionAttemptRepository",
    'SqlAlchemyTaskRepository',
    'SqlAlchemyTaskAttemptRepository',
    "SqlAlchemyProgressRepository",
    'SqlAlchemyCodeTaskRepository',
    'SqlAlchemyTestCaseRepository',
    'SqlAlchemyCodeSubmissionRepository',
]
