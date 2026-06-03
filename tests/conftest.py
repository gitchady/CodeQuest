import os
from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

os.environ.setdefault(
    'JWT_SECRET_KEY',
    'test-secret-key-for-integration-tests-32-bytes-minimum',
)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.presentation.api.dependencies as api_dependencies
from app.bootstrap.build_submission_queue import build_submission_queue
from app.infrastructure.database.models import (
    Base,
    AnswerOptionModel,
    CourseModel,
    LectureModel,
    ModuleModel,
    ProgressModel,
    QuestionAttemptModel,
    QuestionModel,
    RefreshSessionModel,
    SectionModel,
    UserModel,
    CodeSubmissionModel,
    CodeTaskModel,
    TaskAttemptModel,
    TaskModel,
    TestCaseModel,
)
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.queues.in_memory_submission_queue import InMemorySubmissionQueue
from app.main import create_app


def ensure_safe_test_database_url(database_url: str) -> None:
    if os.environ.get('ALLOW_TEST_DATABASE_DROP') == '1':
        return

    url = make_url(database_url)
    if url.get_backend_name() == 'sqlite':
        return

    database_name = (url.database or '').lower()
    if 'test' in database_name:
        return

    raise RuntimeError(
        'Refusing to drop database schema for non-test database. '
        'Set ALLOW_TEST_DATABASE_DROP=1 to override.'
    )


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def test_engine(tmp_path_factory) -> AsyncIterator:
    database_url = os.environ.get('TEST_DATABASE_URL')
    database_path = None
    if database_url is None:
        database_dir = tmp_path_factory.mktemp("test_db")
        database_path = Path(database_dir) / "test_fastapi_education.db"
        database_url = f"sqlite+aiosqlite:///{database_path}"

    ensure_safe_test_database_url(database_url)
    engine = create_async_engine(database_url, future=True, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if database_path is not None and database_path.exists():
        os.remove(database_path)


@pytest.fixture
def session_factory(test_engine):
    return async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture
async def app(session_factory):
    app = create_app()
    original_session_factory = api_dependencies.SessionFactory
    original_build_submission_queue = api_dependencies.build_submission_queue
    api_dependencies.SessionFactory = session_factory
    api_dependencies.build_submission_queue = InMemorySubmissionQueue
    try:
        yield app
    finally:
        api_dependencies.SessionFactory = original_session_factory
        api_dependencies.build_submission_queue = original_build_submission_queue


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client



@pytest_asyncio.fixture(autouse=True)
async def clear_database(session_factory) -> None:
    async with session_factory() as session:
        for model in [
            AnswerOptionModel,
            RefreshSessionModel,
            QuestionAttemptModel,
            TaskAttemptModel,
            CodeSubmissionModel,
            ProgressModel,
            TestCaseModel,
            CodeTaskModel,
            TaskModel,
            QuestionModel,
            LectureModel,
            SectionModel,
            ModuleModel,
            CourseModel,
            UserModel,
        ]:
            await session.execute(delete(model))
        await session.commit()



@pytest_asyncio.fixture
async def seeded_course_tree(session_factory, seeded_admin_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_admin_user.id,
            title='FastAPI course',
            description='Clean architecture in practice.',
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title='MVP stage',
            description='Content, users and access.',
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title='Auth section',
            description='JWT and route protection.',
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title='Bearer token in practice',
            content='Lecture content',
            position=1,
        )
        session.add_all([course, module, section, lecture])
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
        course_title='FastAPI course',
        lecture_content='Lecture content',
    )


@pytest_asyncio.fixture
async def seeded_student_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email='student@example.com',
            hashed_password=hasher.hash('strongpassword123'),
            role='student',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def seeded_admin_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email='admin@example.com',
            hashed_password=hasher.hash('strongpassword123'),
            role='admin',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def student_auth_headers(client, seeded_student_user):
    response = await client.post(
        '/api/auth/login',
        json={
            'email': 'student@example.com',
            'password': 'strongpassword123',
        },
    )
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest_asyncio.fixture
async def admin_auth_headers(client, seeded_admin_user):
    response = await client.post(
        '/api/auth/login',
        json={
            'email': 'admin@example.com',
            'password': 'strongpassword123',
        },
    )
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}



@pytest_asyncio.fixture
async def seeded_author_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email='author@example.com',
            hashed_password=hasher.hash('strongpassword123'),
            role='author',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def author_auth_headers(client, seeded_author_user):
    response = await client.post(
        '/api/auth/login',
        json={
            'email': 'author@example.com',
            'password': 'strongpassword123',
        },
    )
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest_asyncio.fixture
async def seeded_other_author_user(session_factory):
    hasher = PwdlibPasswordHasher()
    async with session_factory() as session:
        user = UserModel(
            id=str(uuid4()),
            email='other-author@example.com',
            hashed_password=hasher.hash('strongpassword123'),
            role='author',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def other_author_auth_headers(client, seeded_other_author_user):
    response = await client.post(
        '/api/auth/login',
        json={
            'email': 'other-author@example.com',
            'password': 'strongpassword123',
        },
    )
    token = response.json()['access_token']
    return {'Authorization': f'Bearer {token}'}



@pytest_asyncio.fixture
async def seeded_interactive_tree(session_factory, seeded_author_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    lecture_id = str(uuid4())
    question_id = str(uuid4())
    wrong_option_id = str(uuid4())
    correct_option_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_author_user.id,
            title='Interactive FastAPI',
            description='Course with questions inside sections.',
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title='HTTP',
            description='Methods',
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title='Basics',
            description='Intro section',
            position=1,
        )
        lecture = LectureModel(
            id=lecture_id,
            section_id=section_id,
            title='GET and POST',
            content='Lecture content',
            position=1,
        )
        question = QuestionModel(
            id=question_id,
            section_id=section_id,
            text='Which method reads a resource?',
            position=1,
            question_type='single_choice',
            max_attempts=2,
            reward_points=5,
        )
        wrong_option = AnswerOptionModel(
            id=wrong_option_id,
            question_id=question_id,
            text='POST',
            position=1,
            is_correct=False,
        )
        correct_option = AnswerOptionModel(
            id=correct_option_id,
            question_id=question_id,
            text='GET',
            position=2,
            is_correct=True,
        )

        session.add_all(
            [
                course,
                module,
                section,
                lecture,
                question,
                wrong_option,
                correct_option,
            ]
        )
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        lecture_id=lecture_id,
        question_id=question_id,
        wrong_option_id=wrong_option_id,
        correct_option_id=correct_option_id,
    )


@pytest_asyncio.fixture
async def seeded_tasks_tree(session_factory, seeded_author_user):
    course_id = str(uuid4())
    module_id = str(uuid4())
    section_id = str(uuid4())
    task_id = str(uuid4())
    code_task_id = str(uuid4())

    async with session_factory() as session:
        course = CourseModel(
            id=course_id,
            author_id=seeded_author_user.id,
            title='Tasks course',
            description='Course with task activities.',
        )
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title='Tasks module',
            description='Practice module.',
            position=1,
        )
        section = SectionModel(
            id=section_id,
            module_id=module_id,
            title='Tasks section',
            description='Intro section.',
            position=1,
        )
        task = TaskModel(
            id=task_id,
            section_id=section_id,
            title='HTTP method',
            statement='Enter GET.',
            position=1,
            check_type='exact_match',
            expected_answer='GET',
            accepted_answers=[],
            answer_pattern='',
            max_attempts=2,
            reward_points=3,
        )
        code_task = CodeTaskModel(
            id=code_task_id,
            section_id=section_id,
            title='Sum numbers',
            statement='Read two integers and print their sum.',
            position=2,
            language='python',
            starter_code='a, b = map(int, input().split())',
            max_attempts=2,
            reward_points=5,
            time_limit_seconds=2,
            memory_limit_mb=128,
        )

        session.add_all([course, module, section, task, code_task])
        await session.commit()

    return SimpleNamespace(
        course_id=course_id,
        module_id=module_id,
        section_id=section_id,
        task_id=task_id,
        code_task_id=code_task_id,
    )

@pytest_asyncio.fixture(autouse=True)
async def reset_submission_queue_cache():
    build_submission_queue.cache_clear()
    yield
    build_submission_queue.cache_clear()
