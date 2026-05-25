from app.application.interfaces.repositories.answer_option_repository import AnswerOptionRepository
from app.application.interfaces.repositories.code_task_repository import CodeTaskRepository
from app.application.interfaces.repositories.course_repository import CourseRepository
from app.application.interfaces.repositories.lecture_repository import LectureRepository
from app.application.interfaces.repositories.module_repository import ModuleRepository
from app.application.interfaces.repositories.progress_repository import ProgressRepository
from app.application.interfaces.repositories.question_attempt_repository import QuestionAttemptRepository
from app.application.interfaces.repositories.question_repository import QuestionRepository
from app.application.interfaces.repositories.section_repository import SectionRepository
from app.application.interfaces.repositories.task_attempt_repository import TaskAttemptRepository
from app.application.interfaces.repositories.task_repository import TaskRepository
from app.application.interfaces.repositories.test_case_repository import TestCaseRepository
from app.application.interfaces.repositories.user_repository import UserRepository
from app.application.interfaces.repositories.code_submission_repository import (
    CodeSubmissionRepository,
)

__all__ = [
    'CourseRepository',
    'ModuleRepository',
    'SectionRepository',
    'LectureRepository',
    'QuestionRepository',
    'AnswerOptionRepository',
    'UserRepository',
    'QuestionAttemptRepository',
    'TaskRepository',
    'TaskAttemptRepository',
    'ProgressRepository',
    'CodeTaskRepository',
    'TestCaseRepository',
    'CodeSubmissionRepository',
]