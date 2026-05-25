class DomainError(Exception):
    """Base exception for domain-layer violations."""


class InvalidCourseError(DomainError):
    pass


class InvalidModuleError(DomainError):
    pass


class InvalidSectionError(DomainError):
    pass


class InvalidLectureError(DomainError):
    pass


class InvalidUserError(DomainError):
    pass


class SectionQuestionAlreadyAttachedError(DomainError):
    pass


class SectionQuestionNotAttachedError(DomainError):
    pass


class InvalidQuestionError(DomainError):
    pass


class InvalidAnswerOptionError(DomainError):
    pass


class InvalidQuestionAttemptError(DomainError):
    pass


class QuestionAttemptLimitExceededError(DomainError):
    pass


class InvalidQuestionResultError(DomainError):
    pass


class QuestionAlreadySolvedError(DomainError):
    pass


class InvalidProgressError(DomainError):
    pass


class InvalidTaskError(DomainError):
    pass


class SectionTaskAlreadyAttachedError(DomainError):
    pass


class SectionTaskNotAttachedError(DomainError):
    pass


class InvalidTaskAttemptError(DomainError):
    pass


class TaskAttemptLimitExceededError(DomainError):
    pass


class TaskAlreadySolvedError(DomainError):
    pass


class InvalidCodeTaskError(DomainError):
    pass


class SectionCodeTaskAlreadyAttachedError(DomainError):
    pass


class SectionCodeTaskNotAttachedError(DomainError):
    pass


class InvalidCodeSubmissionError(DomainError):
    pass


class CodeSubmissionLimitExceededError(DomainError):
    pass


class CodeTaskAlreadySolvedError(DomainError):
    pass


class InvalidTestCaseError(DomainError):
    pass

class InvalidExecutionResultError(DomainError):
    pass