from uuid import uuid4

import pytest

from app.application.exceptions import (
    CourseNotFoundError,
    LectureNotFoundError,
    ModuleNotFoundError,
    SectionNotFoundError,
)
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.courses.create_course import (
    CreateCourseCommand,
    CreateCourseUseCase,
)
from app.application.use_cases.courses.update_course import (
    UpdateCourseCommand,
    UpdateCourseUseCase,
)
from app.application.use_cases.lectures.create_lecture import (
    CreateLectureCommand,
    CreateLectureUseCase,
)
from app.application.use_cases.lectures.update_lecture import (
    UpdateLectureCommand,
    UpdateLectureUseCase,
)
from app.application.use_cases.modules.create_module import (
    CreateModuleCommand,
    CreateModuleUseCase,
)
from app.application.use_cases.modules.update_module import (
    UpdateModuleCommand,
    UpdateModuleUseCase,
)
from app.application.use_cases.sections.create_section import (
    CreateSectionCommand,
    CreateSectionUseCase,
)
from app.application.use_cases.sections.update_section import (
    UpdateSectionCommand,
    UpdateSectionUseCase,
)
from app.domain.entities.course import Course
from app.domain.entities.lecture import Lecture
from app.domain.entities.module import Module
from app.domain.entities.section import Section



from app.domain.entities.user import User, UserRole


def make_author() -> User:
    return User(
        id=uuid4(),
        email='author@example.com',
        hashed_password='hashed-password',
        role=UserRole.AUTHOR,
    )


def make_owned_course(author: User) -> Course:
    return Course(
        id=uuid4(),
        author_id=author.id,
        title='Course',
        description='Description',
    )


class FakeCourseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, course_id):
        return self.items.get(course_id)

    async def list(self):
        return list(self.items.values())

    async def add(self, course) -> None:
        self.items[course.id] = course

    async def update(self, course) -> None:
        self.items[course.id] = course

    async def remove(self, course_id) -> None:
        self.items.pop(course_id, None)


class FakeModuleRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, module_id):
        return self.items.get(module_id)

    async def get_by_ids(self, module_ids):
        return [self.items[module_id] for module_id in module_ids if module_id in self.items]

    async def add(self, module) -> None:
        self.items[module.id] = module

    async def update(self, module) -> None:
        self.items[module.id] = module

    async def remove(self, module_id) -> None:
        self.items.pop(module_id, None)


class FakeSectionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, section_id):
        return self.items.get(section_id)

    async def get_by_ids(self, section_ids):
        return [self.items[section_id] for section_id in section_ids if section_id in self.items]

    async def add(self, section) -> None:
        self.items[section.id] = section

    async def update(self, section) -> None:
        self.items[section.id] = section

    async def remove(self, section_id) -> None:
        self.items.pop(section_id, None)


class FakeLectureRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, lecture_id):
        return self.items.get(lecture_id)

    async def get_by_ids(self, lecture_ids):
        return [self.items[lecture_id] for lecture_id in lecture_ids if lecture_id in self.items]

    async def add(self, lecture) -> None:
        self.items[lecture.id] = lecture

    async def update(self, lecture) -> None:
        self.items[lecture.id] = lecture

    async def remove(self, lecture_id) -> None:
        self.items.pop(lecture_id, None)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.modules = FakeModuleRepository()
        self.sections = FakeSectionRepository()
        self.lectures = FakeLectureRepository()
        self.users = None
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
async def test_create_course_adds_course_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = CreateCourseUseCase(uow=uow)

    result = await use_case.execute(
        CreateCourseCommand(
            actor=actor,
            title='FastAPI course',
            description='Clean architecture in practice.',
        )
    )

    assert result.id in uow.courses.items
    assert result.author_id == actor.id
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_course_changes_existing_course() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = Course(
        id=uuid4(),
        author_id=actor.id,
        title="Old",
        description="Old description",
    )
    await uow.courses.add(course)

    use_case = UpdateCourseUseCase(uow=uow)
    result = await use_case.execute(
        UpdateCourseCommand(
            actor=actor,
            course_id=course.id,
            title="New",
            description="New description",
        )
    )

    assert result.title == "New"
    assert result.description == "New description"
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_course_raises_not_found_when_course_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = UpdateCourseUseCase(uow=uow)

    with pytest.raises(CourseNotFoundError):
        await use_case.execute(
            UpdateCourseCommand(
                actor=actor,
                course_id=uuid4(),
                title="New",
                description="New description",
            )
        )


@pytest.mark.asyncio
async def test_create_module_adds_module_to_course_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    await uow.courses.add(course)

    use_case = CreateModuleUseCase(uow=uow)
    result = await use_case.execute(
        CreateModuleCommand(
            actor=actor,
            course_id=course.id,
            title='Module 1',
            description='Module description',
            position=1,
        )
    )

    assert result.id in uow.modules.items
    assert result.id in course.module_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_module_raises_not_found_when_course_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = CreateModuleUseCase(uow=uow)

    with pytest.raises(CourseNotFoundError):
        await use_case.execute(
            CreateModuleCommand(
                actor=actor,
                course_id=uuid4(),
                title="Module 1",
                description="Module description",
                position=1,
            )
        )


@pytest.mark.asyncio
async def test_update_module_changes_existing_module() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title="Old module",
        description="Old description",
        position=1,
    )
    await uow.courses.add(course)
    await uow.modules.add(module)

    use_case = UpdateModuleUseCase(uow=uow)
    result = await use_case.execute(
        UpdateModuleCommand(
            actor=actor,
            module_id=module.id,
            title="New module",
            description="New description",
            position=2,
        )
    )

    assert result.title == "New module"
    assert result.description == "New description"
    assert result.position == 2
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_module_raises_not_found_when_module_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = UpdateModuleUseCase(uow=uow)

    with pytest.raises(ModuleNotFoundError):
        await use_case.execute(
            UpdateModuleCommand(
                actor=actor,
                module_id=uuid4(),
                title="New module",
                description="New description",
                position=2,
            )
        )


@pytest.mark.asyncio
async def test_create_section_adds_section_to_module_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module',
        description='Description',
        position=1,
    )
    await uow.courses.add(course)
    await uow.modules.add(module)

    use_case = CreateSectionUseCase(uow=uow)
    result = await use_case.execute(
        CreateSectionCommand(
            actor=actor,
            module_id=module.id,
            title='Section 1',
            description='Section description',
            position=1,
        )
    )

    assert result.id in uow.sections.items
    assert result.id in module.section_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_section_raises_not_found_when_module_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = CreateSectionUseCase(uow=uow)

    with pytest.raises(ModuleNotFoundError):
        await use_case.execute(
            CreateSectionCommand(
                actor=actor,
                module_id=uuid4(),
                title="Section 1",
                description="Section description",
                position=1,
            )
        )


@pytest.mark.asyncio
async def test_update_section_changes_existing_section() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title="Module",
        description="Description",
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title="Old section",
        description="Old description",
        position=1,
    )
    module.add_section(section.id)
    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)

    use_case = UpdateSectionUseCase(uow=uow)
    result = await use_case.execute(
        UpdateSectionCommand(
            actor=actor,
            section_id=section.id,
            title="New section",
            description="New description",
            position=2,
        )
    )

    assert result.title == "New section"
    assert result.description == "New description"
    assert result.position == 2
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_section_raises_not_found_when_section_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = UpdateSectionUseCase(uow=uow)

    with pytest.raises(SectionNotFoundError):
        await use_case.execute(
            UpdateSectionCommand(
                actor=actor,
                section_id=uuid4(),
                title="New section",
                description="New description",
                position=2,
            )
        )


@pytest.mark.asyncio
async def test_create_lecture_adds_lecture_to_section_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title="Module",
        description="Description",
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title="Section",
        description="Description",
        position=1,
    )
    module.add_section(section.id)
    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)

    use_case = CreateLectureUseCase(uow=uow)
    result = await use_case.execute(
        CreateLectureCommand(
            actor=actor,
            section_id=section.id,
            title="Lecture 1",
            content="Lecture content",
            position=1,
        )
    )

    assert result.id in uow.lectures.items
    assert result.id in section.lecture_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_lecture_raises_not_found_when_section_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = CreateLectureUseCase(uow=uow)

    with pytest.raises(SectionNotFoundError):
        await use_case.execute(
            CreateLectureCommand(
                actor=actor,
                section_id=uuid4(),
                title="Lecture 1",
                content="Lecture content",
                position=1,
            )
        )


@pytest.mark.asyncio
async def test_update_lecture_changes_existing_lecture() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title="Module",
        description="Description",
        position=1,
    )
    section = Section(
        id=uuid4(),
        module_id=module.id,
        title="Section",
        description="Description",
        position=1,
    )
    lecture = Lecture(
        id=uuid4(),
        section_id=section.id,
        title="Old lecture",
        content="Old content",
        position=1,
    )
    module.add_section(section.id)
    section.add_lecture(lecture.id)
    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.lectures.add(lecture)

    use_case = UpdateLectureUseCase(uow=uow)
    result = await use_case.execute(
        UpdateLectureCommand(
            actor=actor,
            lecture_id=lecture.id,
            title="New lecture",
            content="New content",
            position=2,
        )
    )

    assert result.title == "New lecture"
    assert result.content == "New content"
    assert result.position == 2
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_lecture_raises_not_found_when_lecture_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = UpdateLectureUseCase(uow=uow)

    with pytest.raises(LectureNotFoundError):
        await use_case.execute(
            UpdateLectureCommand(
                actor=actor,
                lecture_id=uuid4(),
                title="New lecture",
                content="New content",
                position=2,
            )
        )
