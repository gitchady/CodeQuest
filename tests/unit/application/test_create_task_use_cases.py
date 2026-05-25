from uuid import uuid4

import pytest

from app.application.exceptions import RetryableExecutionError
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.code_submissions.submit_code_submission import (
    SubmitCodeSubmissionCommand,
    SubmitCodeSubmissionUseCase,
)
from app.application.use_cases.code_tasks.create_code_task import (
    CreateCodeTaskCommand,
    CreateCodeTaskUseCase,
)
from app.application.use_cases.tasks.create_task import (
    CreateTaskCommand,
    CreateTaskUseCase,
)
from app.application.use_cases.tasks.update_task import (
    UpdateTaskCommand,
    UpdateTaskUseCase,
)
from app.application.use_cases.test_cases.create_test_case import (
    CreateTestCaseCommand,
    CreateTestCaseUseCase,
)
from app.domain.entities.code_task import CodeTask, CodeTaskLanguage
from app.domain.entities.course import Course
from app.domain.entities.module import Module
from app.domain.entities.progress import Progress
from app.domain.entities.section import Section
from app.domain.entities.task import Task, TaskCheckType
from app.domain.entities.user import User, UserRole


def make_author() -> User:
    return User(
        id=uuid4(),
        email='author@example.com',
        hashed_password='hashed-password',
        role=UserRole.AUTHOR,
    )


def make_student() -> User:
    return User(
        id=uuid4(),
        email='student@example.com',
        hashed_password='hashed-password',
        role=UserRole.STUDENT,
    )


def make_owned_course(author: User) -> Course:
    return Course(
        id=uuid4(),
        author_id=author.id,
        title='Course',
        description='Description',
    )


async def seed_course_tree_for_code_task(
        uow,
        actor: User,
        code_task: CodeTask,
) -> Section:
    course = make_owned_course(actor)
    module = Module(
        id=uuid4(),
        course_id=course.id,
        title='Module',
        description='Description',
        position=1,
    )
    section = Section(
        id=code_task.section_id,
        module_id=module.id,
        title='Section',
        description='Description',
        position=1,
    )

    module.add_section(section.id)
    section.add_code_task(code_task.id)

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    return section


class FakeCourseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, course_id):
        return self.items.get(course_id)

    async def add(self, course) -> None:
        self.items[course.id] = course

    async def update(self, course) -> None:
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


class FakeTaskRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, task_id):
        return self.items.get(task_id)

    async def add(self, task) -> None:
        self.items[task.id] = task

    async def update(self, task) -> None:
        self.items[task.id] = task


class FakeCodeTaskRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, code_task_id):
        return self.items.get(code_task_id)

    async def add(self, code_task) -> None:
        self.items[code_task.id] = code_task

    async def update(self, code_task) -> None:
        self.items[code_task.id] = code_task


class FakeTestCaseRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, test_case_id):
        return self.items.get(test_case_id)

    async def list_by_code_task_id(self, code_task_id):
        return [
            item for item in self.items.values()
            if item.code_task_id == code_task_id
        ]

    async def add(self, test_case) -> None:
        self.items[test_case.id] = test_case

    async def update(self, test_case) -> None:
        self.items[test_case.id] = test_case


class FakeCodeSubmissionRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_id(self, submission_id):
        return self.items.get(submission_id)

    async def list_by_code_task_id(self, code_task_id):
        return [
            item for item in self.items.values()
            if item.code_task_id == code_task_id
        ]

    async def list_by_code_task_and_student_id(self, code_task_id, student_id):
        return [
            item for item in self.items.values()
            if item.code_task_id == code_task_id
            and item.student_id == student_id
        ]

    async def add(self, submission) -> None:
        self.items[submission.id] = submission

    async def update(self, submission) -> None:
        self.items[submission.id] = submission


class FakeTaskAttemptRepository:
    def __init__(self) -> None:
        self.items = {}

    async def exists_by_task_id(self, task_id) -> bool:
        return any(item.task_id == task_id for item in self.items.values())


class FakeProgressRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_by_student_and_course(self, student_id, course_id):
        return self.items.get((student_id, course_id))

    async def add(self, progress: Progress) -> None:
        self.items[(progress.student_id, progress.course_id)] = progress

    async def update(self, progress: Progress) -> None:
        self.items[(progress.student_id, progress.course_id)] = progress


class FakeSubmissionQueue:
    def __init__(self) -> None:
        self.items = []
        self.commit_states = []

    async def enqueue(self, submission_id) -> None:
        self.items.append(submission_id)


class RecordingSubmissionQueue:
    def __init__(self, uow: 'FakeTasksUnitOfWork') -> None:
        self.uow = uow
        self.items = []
        self.commit_states = []

    async def enqueue(self, submission_id) -> None:
        self.items.append(submission_id)
        self.commit_states.append(self.uow.committed)


class FailingSubmissionQueue:
    async def enqueue(self, submission_id) -> None:
        raise RuntimeError('Redis is unavailable')


class FakeTasksUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.courses = FakeCourseRepository()
        self.modules = FakeModuleRepository()
        self.sections = FakeSectionRepository()
        self.tasks = FakeTaskRepository()
        self.code_tasks = FakeCodeTaskRepository()
        self.test_cases = FakeTestCaseRepository()
        self.code_submissions = FakeCodeSubmissionRepository()
        self.task_attempts = FakeTaskAttemptRepository()
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
async def test_create_task_adds_task_and_updates_section() -> None:
    uow = FakeTasksUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
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

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)

    use_case = CreateTaskUseCase(uow=uow)
    result = await use_case.execute(
        CreateTaskCommand(
            actor=actor,
            section_id=section.id,
            title='HTTP method',
            statement='Enter GET.',
            position=1,
            check_type=TaskCheckType.EXACT_MATCH,
            expected_answer='GET',
            max_attempts=2,
            reward_points=3,
        )
    )

    assert result.id in uow.tasks.items
    assert result.id in section.task_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_update_task_changes_checking_policy_fields_before_attempts() -> None:
    uow = FakeTasksUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
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
    task = Task(
        id=uuid4(),
        section_id=section.id,
        title='HTTP method',
        statement='Enter GET.',
        position=1,
        check_type=TaskCheckType.EXACT_MATCH,
        expected_answer='GET',
        max_attempts=1,
        reward_points=1,
    )
    module.add_section(section.id)
    section.add_task(task.id)

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)
    await uow.tasks.add(task)

    use_case = UpdateTaskUseCase(uow=uow)
    result = await use_case.execute(
        UpdateTaskCommand(
            actor=actor,
            task_id=task.id,
            title='HTTP methods',
            statement='Enter one valid read method.',
            position=2,
            check_type=TaskCheckType.ANY_OF,
            accepted_answers=['GET', 'HEAD'],
            max_attempts=3,
            reward_points=5,
        )
    )

    assert result.title == 'HTTP methods'
    assert result.statement == 'Enter one valid read method.'
    assert result.position == 2
    assert result.check_type is TaskCheckType.ANY_OF
    assert result.expected_answer == ''
    assert result.accepted_answers == ['GET', 'HEAD']
    assert result.max_attempts == 3
    assert result.reward_points == 5
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_code_task_adds_code_task_and_updates_section() -> None:
    uow = FakeTasksUnitOfWork()
    actor = make_author()
    course = make_owned_course(actor)
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

    await uow.courses.add(course)
    await uow.modules.add(module)
    await uow.sections.add(section)

    use_case = CreateCodeTaskUseCase(uow=uow)
    result = await use_case.execute(
        CreateCodeTaskCommand(
            actor=actor,
            section_id=section.id,
            title='Sum numbers',
            statement='Print sum.',
            position=1,
            language=CodeTaskLanguage.PYTHON,
            starter_code='print(1)',
            max_attempts=2,
            reward_points=5,
            time_limit_seconds=2,
            memory_limit_mb=128,
        )
    )

    assert result.id in uow.code_tasks.items
    assert result.id in section.code_task_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_create_test_case_adds_test_case_and_updates_code_task() -> None:
    uow = FakeTasksUnitOfWork()
    actor = make_author()
    code_task = CodeTask(
        id=uuid4(),
        section_id=uuid4(),
        title='Sum numbers',
        statement='Print sum.',
        position=1,
        language=CodeTaskLanguage.PYTHON,
        starter_code='print(1)',
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    await uow.code_tasks.add(code_task)
    await seed_course_tree_for_code_task(uow, actor, code_task)

    use_case = CreateTestCaseUseCase(uow=uow)
    result = await use_case.execute(
        CreateTestCaseCommand(
            actor=actor,
            code_task_id=code_task.id,
            position=1,
            input_data='2 3',
            expected_output='5',
            is_hidden=False,
            explanation='basic case',
        )
    )

    assert result.id in uow.test_cases.items
    assert result.id in code_task.test_case_ids
    assert uow.committed is True


@pytest.mark.asyncio
async def test_submit_code_submission_creates_submission_and_enqueues_id() -> None:
    uow = FakeTasksUnitOfWork()
    queue = FakeSubmissionQueue()
    student = make_student()
    code_task = CodeTask(
        id=uuid4(),
        section_id=uuid4(),
        title='Sum numbers',
        statement='Print sum.',
        position=1,
        language=CodeTaskLanguage.PYTHON,
        starter_code='print(1)',
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    await uow.code_tasks.add(code_task)
    await seed_course_tree_for_code_task(uow, make_author(), code_task)

    use_case = SubmitCodeSubmissionUseCase(uow=uow, submission_queue=queue)
    result = await use_case.execute(
        SubmitCodeSubmissionCommand(
            actor=student,
            code_task_id=code_task.id,
            source_code='print(1)',
        )
    )

    assert result.id in uow.code_submissions.items
    assert queue.items == [result.id]
    assert uow.committed is True


@pytest.mark.asyncio
async def test_submit_code_submission_enqueues_only_after_commit() -> None:
    uow = FakeTasksUnitOfWork()
    queue = RecordingSubmissionQueue(uow)
    student = make_student()
    code_task = CodeTask(
        id=uuid4(),
        section_id=uuid4(),
        title='Sum numbers',
        statement='Print sum.',
        position=1,
        language=CodeTaskLanguage.PYTHON,
        starter_code='print(1)',
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    await uow.code_tasks.add(code_task)
    await seed_course_tree_for_code_task(uow, make_author(), code_task)

    use_case = SubmitCodeSubmissionUseCase(uow=uow, submission_queue=queue)
    result = await use_case.execute(
        SubmitCodeSubmissionCommand(
            actor=student,
            code_task_id=code_task.id,
            source_code='print(1)',
        )
    )

    assert queue.items == [result.id]
    assert queue.commit_states == [True]


@pytest.mark.asyncio
async def test_submit_code_submission_marks_submission_error_when_enqueue_fails() -> None:
    uow = FakeTasksUnitOfWork()
    student = make_student()
    code_task = CodeTask(
        id=uuid4(),
        section_id=uuid4(),
        title='Sum numbers',
        statement='Print sum.',
        position=1,
        language=CodeTaskLanguage.PYTHON,
        starter_code='print(1)',
        max_attempts=2,
        reward_points=5,
        time_limit_seconds=2,
        memory_limit_mb=128,
    )

    await uow.code_tasks.add(code_task)
    await seed_course_tree_for_code_task(uow, make_author(), code_task)

    use_case = SubmitCodeSubmissionUseCase(
        uow=uow,
        submission_queue=FailingSubmissionQueue(),
    )

    with pytest.raises(RetryableExecutionError):
        await use_case.execute(
            SubmitCodeSubmissionCommand(
                actor=student,
                code_task_id=code_task.id,
                source_code='print(1)',
            )
        )

    submission = next(iter(uow.code_submissions.items.values()))
    assert submission.status.value == 'error'
