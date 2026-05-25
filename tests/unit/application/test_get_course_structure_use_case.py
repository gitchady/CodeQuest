from uuid import uuid4

import pytest

from app.application.use_cases.courses.get_course_structure import (
    GetCourseStructureQuery,
    GetCourseStructureUseCase,
)
from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.domain.entities.course import Course
from app.domain.entities.lecture import Lecture
from app.domain.entities.module import Module
from app.domain.entities.section import Section
from app.domain.entities.task import Task, TaskCheckType


class CountingRepository:
    def __init__(self, items):
        self.items = {item.id: item for item in items}
        self.get_by_ids_calls = 0

    async def get_by_id(self, item_id):
        return self.items.get(item_id)

    async def get_by_ids(self, item_ids):
        self.get_by_ids_calls += 1
        return [self.items[item_id] for item_id in item_ids if item_id in self.items]


@pytest.mark.asyncio
async def test_get_course_structure_loads_nested_content_in_batches() -> None:
    course = Course(
        id=uuid4(),
        author_id=uuid4(),
        title='Course',
        description='Description',
    )
    module_one = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module 1',
        description='Description',
        position=1,
    )
    module_two = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module 2',
        description='Description',
        position=2,
    )
    sections = [
        Section(
            id=uuid4(),
            module_id=module_one.id,
            title='Section 1',
            description='Description',
            position=1,
        ),
        Section(
            id=uuid4(),
            module_id=module_one.id,
            title='Section 2',
            description='Description',
            position=2,
        ),
        Section(
            id=uuid4(),
            module_id=module_two.id,
            title='Section 3',
            description='Description',
            position=1,
        ),
    ]
    for section in sections[:2]:
        module_one.add_section(section.id)
    module_two.add_section(sections[2].id)
    course.add_module(module_one.id)
    course.add_module(module_two.id)

    lectures = []
    tasks = []
    code_tasks = []
    for index, section in enumerate(sections, start=1):
        lecture = Lecture(
            id=uuid4(),
            section_id=section.id,
            title=f'Lecture {index}',
            content='Content',
            position=1,
        )
        task = Task(
            id=uuid4(),
            section_id=section.id,
            title=f'Task {index}',
            statement='Enter OK.',
            position=1,
            check_type=TaskCheckType.EXACT_MATCH,
            expected_answer='OK',
        )
        code_task = CodeTask(
            id=uuid4(),
            section_id=section.id,
            title=f'Code task {index}',
            statement='Print OK.',
            position=1,
            language=CodeTaskLanguage.PYTHON,
            starter_code='print("OK")',
            max_attempts=1,
            reward_points=1,
            time_limit_seconds=2,
            memory_limit_mb=128,
        )
        section.add_lecture(lecture.id)
        section.add_task(task.id)
        section.add_code_task(code_task.id)
        lectures.append(lecture)
        tasks.append(task)
        code_tasks.append(code_task)

    module_repository = CountingRepository([module_one, module_two])
    section_repository = CountingRepository(sections)
    lecture_repository = CountingRepository(lectures)
    task_repository = CountingRepository(tasks)
    code_task_repository = CountingRepository(code_tasks)

    use_case = GetCourseStructureUseCase(
        course_repository=CountingRepository([course]),
        module_repository=module_repository,
        section_repository=section_repository,
        lecture_repository=lecture_repository,
        task_repository=task_repository,
        code_task_repository=code_task_repository,
    )

    result = await use_case.execute(GetCourseStructureQuery(course_id=course.id))

    assert len(result.modules) == 2
    assert module_repository.get_by_ids_calls == 1
    assert section_repository.get_by_ids_calls == 1
    assert lecture_repository.get_by_ids_calls == 1
    assert task_repository.get_by_ids_calls == 1
    assert code_task_repository.get_by_ids_calls == 1
