from uuid import uuid4

import pytest

from app.application.exceptions import (
    CourseNotFoundError,
    LectureNotFoundError,
    ModuleNotFoundError,
    SectionNotFoundError,
)
from app.application.use_cases.courses.delete_course import (
    DeleteCourseCommand,
    DeleteCourseUseCase,
)
from app.application.use_cases.lectures.delete_lecture import (
    DeleteLectureCommand,
    DeleteLectureUseCase,
)
from app.application.use_cases.modules.delete_module import (
    DeleteModuleCommand,
    DeleteModuleUseCase,
)
from app.application.use_cases.sections.delete_section import (
    DeleteSectionCommand,
    DeleteSectionUseCase,
)
from app.domain.entities.lecture import Lecture
from app.domain.entities.module import Module
from app.domain.entities.section import Section
from tests.unit.application.test_content_write_use_cases import (
    FakeUnitOfWork,
    make_author,
    make_owned_course,
)


@pytest.mark.asyncio
async def test_delete_course_removes_course_and_commits() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
    await uow.courses.add(course)

    use_case = DeleteCourseUseCase(uow=uow)
    await use_case.execute(DeleteCourseCommand(actor=actor, course_id=course.id))

    assert course.id not in uow.courses.items
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_course_raises_not_found_when_course_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = DeleteCourseUseCase(uow=uow)

    with pytest.raises(CourseNotFoundError):
        await use_case.execute(DeleteCourseCommand(actor=actor, course_id=uuid4()))


@pytest.mark.asyncio
async def test_delete_module_removes_module_and_updates_course() -> None:
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
    course.add_module(module.id)
    await uow.courses.add(course)
    await uow.modules.add(module)

    use_case = DeleteModuleUseCase(uow=uow)
    await use_case.execute(DeleteModuleCommand(actor=actor, module_id=module.id))

    assert module.id not in uow.modules.items
    assert module.id not in course.module_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_module_raises_not_found_when_module_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = DeleteModuleUseCase(uow=uow)

    with pytest.raises(ModuleNotFoundError):
        await use_case.execute(DeleteModuleCommand(actor=actor, module_id=uuid4()))


@pytest.mark.asyncio
async def test_delete_section_removes_section_and_updates_module() -> None:
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

    use_case = DeleteSectionUseCase(uow=uow)
    await use_case.execute(DeleteSectionCommand(actor=actor, section_id=section.id))

    assert section.id not in uow.sections.items
    assert section.id not in module.section_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_section_raises_not_found_when_section_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = DeleteSectionUseCase(uow=uow)

    with pytest.raises(SectionNotFoundError):
        await use_case.execute(DeleteSectionCommand(actor=actor, section_id=uuid4()))


@pytest.mark.asyncio
async def test_delete_lecture_removes_lecture_and_updates_section() -> None:
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
        title="Lecture",
        content="Content",
        position=1,
    )
    module.add_section(section.id)
    section.add_lecture(lecture.id)
    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.lectures.add(lecture)

    use_case = DeleteLectureUseCase(uow=uow)
    await use_case.execute(DeleteLectureCommand(actor=actor, lecture_id=lecture.id))

    assert lecture.id not in uow.lectures.items
    assert lecture.id not in section.lecture_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_lecture_raises_not_found_when_lecture_is_missing() -> None:
    uow = FakeUnitOfWork()
    actor = make_author()
    use_case = DeleteLectureUseCase(uow=uow)

    with pytest.raises(LectureNotFoundError):
        await use_case.execute(DeleteLectureCommand(actor=actor, lecture_id=uuid4()))
