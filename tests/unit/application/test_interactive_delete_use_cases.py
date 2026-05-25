from uuid import uuid4

import pytest

from app.application.exceptions import (
    AnswerOptionNotFoundError,
    QuestionAlreadyUsedError,
    QuestionNotFoundError,
)
from app.application.use_cases.answer_options.delete_answer_option import (
    DeleteAnswerOptionCommand,
    DeleteAnswerOptionUseCase,
)
from app.application.use_cases.questions.delete_question import (
    DeleteQuestionCommand,
    DeleteQuestionUseCase,
)
from app.domain.entities.answer_option import AnswerOption
from app.domain.entities.course import Course
from app.domain.entities.module import Module
from app.domain.entities.question import Question, QuestionType
from app.domain.entities.section import Section
from app.domain.exceptions import InvalidQuestionError
from tests.unit.application.test_content_write_use_cases import make_author


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


class FakeSectionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, section_id):
        return self.items.get(section_id)

    async def add(self, section) -> None:
        self.items[section.id] = section

    async def update(self, section) -> None:
        self.items[section.id] = section


class FakeQuestionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, question_id):
        return self.items.get(question_id)

    async def add(self, question) -> None:
        self.items[question.id] = question

    async def update(self, question) -> None:
        self.items[question.id] = question

    async def remove(self, question_id) -> None:
        self.items.pop(question_id, None)


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

    async def remove(self, answer_option_id) -> None:
        self.items.pop(answer_option_id, None)


class FakeQuestionAttemptRepository:
    def __init__(self) -> None:
        self.used_question_ids = set()

    async def exists_by_question_id(self, question_id) -> bool:
        return question_id in self.used_question_ids


class FakeInteractiveDeleteUnitOfWork:
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.modules = FakeModuleRepository()
        self.sections = FakeSectionRepository()
        self.questions = FakeQuestionRepository()
        self.answer_options = FakeAnswerOptionRepository()
        self.question_attempts = FakeQuestionAttemptRepository()
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


async def seed_interactive_tree(uow: FakeInteractiveDeleteUnitOfWork, actor):
    course = Course(
        id=uuid4(),
        author_id=actor.id,
        title='Course',
        description='Description',
    )
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module',
        description='Description',
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title='Section',
        description='Description',
        position=1,
    )
    module.add_section(section.id)

    question = Question(
        id=uuid4(),
        section_id=section.id,
        text='Which method reads a resource?',
        position=1,
        question_type=QuestionType.SINGLE_CHOICE,
        max_attempts=2,
        reward_points=5,
    )
    section.add_question(question.id)

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.questions.add(question)
    return course, module, section, question


@pytest.mark.asyncio
async def test_delete_question_removes_question_and_updates_section() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    _, _, section, question = await seed_interactive_tree(uow, actor)

    use_case = DeleteQuestionUseCase(uow)
    await use_case.execute(DeleteQuestionCommand(actor=actor, question_id=question.id))

    assert question.id not in uow.questions.items
    assert question.id not in section.question_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_question_raises_when_question_is_missing() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    use_case = DeleteQuestionUseCase(uow)

    with pytest.raises(QuestionNotFoundError):
        await use_case.execute(DeleteQuestionCommand(actor=actor, question_id=uuid4()))


@pytest.mark.asyncio
async def test_delete_question_raises_when_question_already_has_attempts() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    _, _, section, question = await seed_interactive_tree(uow, actor)
    uow.question_attempts.used_question_ids.add(question.id)

    use_case = DeleteQuestionUseCase(uow)

    with pytest.raises(QuestionAlreadyUsedError):
        await use_case.execute(DeleteQuestionCommand(actor=actor, question_id=question.id))

    assert question.id in uow.questions.items
    assert question.id in section.question_ids


@pytest.mark.asyncio
async def test_delete_answer_option_removes_option_when_question_stays_valid() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    _, _, _, question = await seed_interactive_tree(uow, actor)
    wrong_option_1 = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='POST',
        position=1,
        is_correct=False,
    )
    wrong_option_2 = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='PUT',
        position=2,
        is_correct=False,
    )
    correct_option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='GET',
        position=3,
        is_correct=True,
    )
    question.answer_option_ids = [wrong_option_1.id, wrong_option_2.id, correct_option.id]
    await uow.answer_options.add(wrong_option_1)
    await uow.answer_options.add(wrong_option_2)
    await uow.answer_options.add(correct_option)

    use_case = DeleteAnswerOptionUseCase(uow)
    await use_case.execute(
        DeleteAnswerOptionCommand(actor=actor, answer_option_id=wrong_option_1.id)
    )

    assert wrong_option_1.id not in uow.answer_options.items
    assert wrong_option_1.id not in question.answer_option_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_answer_option_raises_when_option_is_missing() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    use_case = DeleteAnswerOptionUseCase(uow)

    with pytest.raises(AnswerOptionNotFoundError):
        await use_case.execute(
            DeleteAnswerOptionCommand(actor=actor, answer_option_id=uuid4())
        )


@pytest.mark.asyncio
async def test_delete_answer_option_raises_when_question_already_has_attempts() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    _, _, _, question = await seed_interactive_tree(uow, actor)
    wrong_option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='POST',
        position=1,
        is_correct=False,
    )
    correct_option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='GET',
        position=2,
        is_correct=True,
    )
    question.answer_option_ids = [wrong_option.id, correct_option.id]
    await uow.answer_options.add(wrong_option)
    await uow.answer_options.add(correct_option)
    uow.question_attempts.used_question_ids.add(question.id)

    use_case = DeleteAnswerOptionUseCase(uow)

    with pytest.raises(QuestionAlreadyUsedError):
        await use_case.execute(
            DeleteAnswerOptionCommand(actor=actor, answer_option_id=wrong_option.id)
        )

    assert wrong_option.id in uow.answer_options.items
    assert wrong_option.id in question.answer_option_ids


@pytest.mark.asyncio
async def test_delete_answer_option_raises_when_question_becomes_invalid() -> None:
    uow = FakeInteractiveDeleteUnitOfWork()
    actor = make_author()
    _, _, _, question = await seed_interactive_tree(uow, actor)
    wrong_option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='POST',
        position=1,
        is_correct=False,
    )
    correct_option = AnswerOption(
        id=uuid4(),
        question_id=question.id,
        text='GET',
        position=2,
        is_correct=True,
    )
    question.answer_option_ids = [wrong_option.id, correct_option.id]
    await uow.answer_options.add(wrong_option)
    await uow.answer_options.add(correct_option)

    use_case = DeleteAnswerOptionUseCase(uow)

    with pytest.raises(InvalidQuestionError):
        await use_case.execute(
            DeleteAnswerOptionCommand(actor=actor, answer_option_id=wrong_option.id)
        )

    assert wrong_option.id in uow.answer_options.items
    assert uow.committed is False
