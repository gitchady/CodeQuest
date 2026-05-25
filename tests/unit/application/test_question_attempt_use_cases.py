from uuid import uuid4

import pytest

from app.application.use_cases.question_attempts.start_question_attempt import (
    StartQuestionAttemptCommand,
    StartQuestionAttemptUseCase,
)
from app.application.use_cases.question_attempts.submit_question_answer import (
    SubmitQuestionAnswerCommand,
    SubmitQuestionAnswerUseCase,
)
from app.application.use_cases.question_attempts.get_question_attempt_result import (
    GetQuestionAttemptResultCommand,
    GetQuestionAttemptResultUseCase,
)
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.course import Course
from app.domain.entities.module import Module
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.question_attempt import QuestionAttempt, QuestionResultStatus
from app.domain.entities.section import Section
from app.domain.entities.user import User, UserRole


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, question_id):
        return self.items.get(question_id)

    async def add(self, question) -> None:
        self.items[question.id] = question

    async def update(self, question) -> None:
        self.items[question.id] = question


class FakeAnswerOptionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, answer_option_id):
        return self.items.get(answer_option_id)

    async def get_by_ids(self, answer_option_ids):
        return [
            self.items[answer_option_id]
            for answer_option_id in answer_option_ids
            if answer_option_id in self.items
        ]

    async def add(self, answer_option) -> None:
        self.items[answer_option.id] = answer_option

    async def update(self, answer_option) -> None:
        self.items[answer_option.id] = answer_option


class FakeQuestionAttemptRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, attempt_id):
        return self.items.get(attempt_id)

    async def get_by_student_and_question(self, student_id, question_id):
        attempts = [
            item
            for item in self.items.values()
            if item.student_id == student_id and item.question_id == question_id
        ]
        return sorted(attempts, key=lambda item: item.attempt_number)

    async def add(self, attempt) -> None:
        self.items[attempt.id] = attempt


class FakeProgressRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_student_and_course(self, student_id, course_id):
        for item in self.items.values():
            if item.student_id == student_id and item.course_id == course_id:
                return item
        return None

    async def add(self, progress) -> None:
        self.items[progress.id] = progress

    async def update(self, progress) -> None:
        self.items[progress.id] = progress


class FakeCourseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, course_id):
        return self.items.get(course_id)

    async def add(self, course) -> None:
        self.items[course.id] = course


class FakeModuleRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, module_id):
        return self.items.get(module_id)

    async def add(self, module) -> None:
        self.items[module.id] = module

    async def update(self, module) -> None:
        self.items[module.id] = module


class FakeSectionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, section_id):
        return self.items.get(section_id)

    async def add(self, section) -> None:
        self.items[section.id] = section

    async def update(self, section) -> None:
        self.items[section.id] = section


class FakeInteractiveUnitOfWork:
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.modules = FakeModuleRepository()
        self.sections = FakeSectionRepository()
        self.questions = FakeQuestionRepository()
        self.answer_options = FakeAnswerOptionRepository()
        self.question_attempts = FakeQuestionAttemptRepository()
        self.progress = FakeProgressRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.mark.asyncio
async def test_start_question_attempt_returns_question_state() -> None:
    uow = FakeInteractiveUnitOfWork()
    student = User(
        id=uuid4(),
        email='student@example.com',
        hashed_password='hashed',
        role=UserRole.STUDENT,
    )
    question = Question(
        id=uuid4(),
        section_id=uuid4(),
        text='Which method reads a resource?',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        max_attempts=2,
        reward_points=5,
    )
    wrong_option = AnswerOption(
        id=uuid4(), question_id=question.id, text='POST', position=1, is_correct=False
    )
    correct_option = AnswerOption(
        id=uuid4(), question_id=question.id, text='GET', position=2, is_correct=True
    )
    question.answer_option_ids = [wrong_option.id, correct_option.id]

    await uow.questions.add(question)
    await uow.answer_options.add(wrong_option)
    await uow.answer_options.add(correct_option)

    use_case = StartQuestionAttemptUseCase(uow)
    result = await use_case.execute(
        StartQuestionAttemptCommand(actor=student, question_id=question.id)
    )

    assert result.question_id == question.id
    assert result.can_submit is True
    assert result.is_solved is False
    assert result.attempts_used == 0
    assert len(result.answer_options) == 2

@pytest.mark.asyncio
async def test_submit_question_answer_creates_attempt_and_updates_progress() -> None:
    uow = FakeInteractiveUnitOfWork()
    student = User(
        id=uuid4(),
        email='student@example.com',
        hashed_password='hashed',
        role=UserRole.STUDENT,
    )
    course_id = uuid4()
    section = Section(
        id=uuid4(),
        module_id=uuid4(),
        title='HTTP',
        description='Methods',
        position=1,
    )
    module = Module(
        id=section.module_id,
        course_id=course_id,
        title='Basics',
        description='Base module',
        position=1,
        section_ids=[section.id],
    )
    question = Question(
        id=uuid4(),
        section_id=section.id,
        text='Which method reads a resource?',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        max_attempts=2,
        reward_points=5,
    )
    correct_option = AnswerOption(
        id=uuid4(), question_id=question.id, text='GET', position=1, is_correct=True
    )
    wrong_option = AnswerOption(
        id=uuid4(), question_id=question.id, text='POST', position=2, is_correct=False
    )
    question.answer_option_ids = [correct_option.id, wrong_option.id]
    section.question_ids = [question.id]

    await uow.questions.add(question)
    await uow.answer_options.add(correct_option)
    await uow.answer_options.add(wrong_option)
    await uow.sections.add(section)
    await uow.modules.add(module)

    use_case = SubmitQuestionAnswerUseCase(uow)
    result = await use_case.execute(
        SubmitQuestionAnswerCommand(
            actor=student,
            question_id=question.id,
            selected_option_ids=[correct_option.id],
        )
    )

    progress = await uow.progress.get_by_student_and_course(student.id, course_id)

    assert result.result_status is QuestionResultStatus.CORRECT
    assert result.awarded_points == 5
    assert progress is not None
    assert question.id in progress.completed_question_ids
    assert section.id in progress.completed_section_ids
    assert module.id in progress.completed_module_ids
    assert progress.total_points == 5
    assert uow.committed is True


@pytest.mark.asyncio
async def test_get_question_attempt_result_allows_owner_author() -> None:
    uow = FakeInteractiveUnitOfWork()
    author = User(
        id=uuid4(),
        email='author@example.com',
        hashed_password='hashed',
        role=UserRole.AUTHOR,
    )
    course = Course(
        id=uuid4(),
        author_id=author.id,
        title='Course',
        description='Description',
    )
    module = Module(id=uuid4(), course_id=course.id, title='M', description='D', position=1)
    section = Section(id=uuid4(), module_id=module.id, title='S', description='D', position=1)
    question = Question(id=uuid4(), section_id=section.id, text='Q', position=1)
    attempt = QuestionAttempt(
        id=uuid4(),
        question_id=question.id,
        student_id=uuid4(),
        attempt_number=1,
        selected_option_ids=[uuid4()],
    )
    attempt.apply_result(QuestionResultStatus.CORRECT, 5)

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.questions.add(question)
    await uow.question_attempts.add(attempt)

    use_case = GetQuestionAttemptResultUseCase(uow)
    result = await use_case.execute(
        GetQuestionAttemptResultCommand(actor=author, attempt_id=attempt.id)
    )

    assert result.attempt_id == attempt.id
    assert result.result_status is QuestionResultStatus.CORRECT