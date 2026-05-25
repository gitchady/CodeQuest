class ApplicationError(Exception):
    """Base exception for application-layer errors."""


class CourseNotFoundError(ApplicationError):
    pass


class ModuleNotFoundError(ApplicationError):
    pass


class SectionNotFoundError(ApplicationError):
    pass


class LectureNotFoundError(ApplicationError):
    pass


class UserAlreadyExistsError(ApplicationError):
    pass


class InvalidCredentialsError(ApplicationError):
    pass

class QuestionNotFoundError(ApplicationError):
    pass


class PermissionDeniedError(ApplicationError):
    pass

class AnswerOptionNotFoundError(ApplicationError):
    pass

class QuestionAlreadyUsedError(ApplicationError):
    pass

class QuestionAttemptNotFoundError(ApplicationError):
    pass

class TaskNotFoundError(ApplicationError):
    pass


class TaskAlreadyUsedError(ApplicationError):
    pass

class CodeSubmissionNotFoundError(ApplicationError):
    pass

class CodeTaskNotFoundError(ApplicationError):
    pass

class CodeTaskAlreadyUsedError(ApplicationError):
    pass

class TestCaseNotFoundError(ApplicationError):
    pass

class RetryableExecutionError(ApplicationError):
    pass