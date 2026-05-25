from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.repositories import (
    SqlAlchemyAnswerOptionRepository,
    SqlAlchemyCourseRepository,
    SqlAlchemyLectureRepository,
    SqlAlchemyModuleRepository,
    SqlAlchemyProgressRepository,
    SqlAlchemyQuestionAttemptRepository,
    SqlAlchemyQuestionRepository,
    SqlAlchemySectionRepository,
    SqlAlchemyUserRepository, SqlAlchemyTaskRepository, SqlAlchemyTaskAttemptRepository,
    SqlAlchemyCodeTaskRepository,
    SqlAlchemyTestCaseRepository,
    SqlAlchemyCodeSubmissionRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        session: AsyncSession | None = None,
    ) -> None:
        self.session_factory = session_factory
        self._external_session = session
        self.session: AsyncSession | None = session

    async def __aenter__(self) -> 'SqlAlchemyUnitOfWork':
        if self.session is None:
            if self.session_factory is None:
                raise RuntimeError('Session factory is required when session is not provided.')
            self.session = self.session_factory()

        self.courses = SqlAlchemyCourseRepository(self.session)
        self.modules = SqlAlchemyModuleRepository(self.session)
        self.sections = SqlAlchemySectionRepository(self.session)
        self.lectures = SqlAlchemyLectureRepository(self.session)
        self.users = SqlAlchemyUserRepository(self.session)
        self.questions = SqlAlchemyQuestionRepository(self.session)
        self.answer_options = SqlAlchemyAnswerOptionRepository(self.session)
        self.question_attempts = SqlAlchemyQuestionAttemptRepository(self.session)
        self.tasks = SqlAlchemyTaskRepository(self.session)
        self.task_attempts = SqlAlchemyTaskAttemptRepository(self.session)
        self.progress = SqlAlchemyProgressRepository(self.session)
        self.code_tasks = SqlAlchemyCodeTaskRepository(self.session)
        self.test_cases = SqlAlchemyTestCaseRepository(self.session)
        self.code_submissions = SqlAlchemyCodeSubmissionRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc_type is not None:
            await self.rollback()
        if self._external_session is None:
            await self.session.close()
            self.session = None

    async def commit(self) -> None:
        if self.session is not None:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()