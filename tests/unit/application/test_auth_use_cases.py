from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest

from app.application.exceptions import UserAlreadyExistsError
from app.application.exceptions import InvalidRefreshTokenError
from app.application.use_cases.auth.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)
from app.application.exceptions import InvalidCredentialsError
from app.application.use_cases.auth.login_user import LoginUserCommand, LoginUserUseCase
from app.application.use_cases.auth.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenUseCase,
)
from app.domain.entities.refresh_session import RefreshSession
from app.domain.entities.user import User, UserRole


class FakeUserRepository:
    def __init__(self) -> None:
        self.items: dict[str, User] = {}

    async def get_by_id(self, user_id):
        for user in self.items.values():
            if user.id == user_id:
                return user
        return None

    async def get_by_email(self, email: str):
        return self.items.get(email)

    async def add(self, user: User) -> None:
        self.items[user.email] = user


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.refresh_sessions = FakeRefreshSessionRepository()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


class StubPasswordHasher:
    def hash(self, raw_password: str) -> str:
        return f'hashed::{raw_password}'

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        return hashed_password == f'hashed::{raw_password}'


class StubTokenService:
    def create_access_token(self, user_id, role: str) -> str:
        return f'access-token-for-{user_id}-{role}'

    def create_refresh_token(self) -> str:
        return f'refresh-token-{uuid4()}'

    def hash_refresh_token(self, token: str) -> str:
        return f'hash::{token}'

    def get_refresh_token_expires_at(self):
        return datetime.now(timezone.utc) + timedelta(days=30)

    def get_user_id(self, token: str):
        raise NotImplementedError


class FakeRefreshSessionRepository:
    def __init__(self) -> None:
        self.items: dict[str, RefreshSession] = {}
        self.locked_token_hashes: list[str] = []

    async def get_by_token_hash_for_update(self, token_hash: str):
        self.locked_token_hashes.append(token_hash)
        return self.items.get(token_hash)

    async def add(self, refresh_session: RefreshSession) -> None:
        self.items[refresh_session.token_hash] = refresh_session

    async def save(self, refresh_session: RefreshSession) -> None:
        self.items[refresh_session.token_hash] = refresh_session

@pytest.mark.asyncio
async def test_register_user_creates_student_and_commits() -> None:
    uow = FakeUnitOfWork()
    use_case = RegisterUserUseCase(uow=uow, password_hasher=StubPasswordHasher())

    result = await use_case.execute(
        RegisterUserCommand(
            email='student@example.com',
            password='secret123',
        )
    )

    assert result.email == 'student@example.com'
    assert result.role is UserRole.STUDENT
    assert result.hashed_password == 'hashed::secret123'
    assert uow.committed is True


@pytest.mark.asyncio
async def test_register_user_raises_error_when_email_already_exists() -> None:
    uow = FakeUnitOfWork()
    existing_user = User(
        id=uuid4(),
        email='student@example.com',
        hashed_password='hashed::secret123',
        role=UserRole.STUDENT,
    )
    await uow.users.add(existing_user)

    use_case = RegisterUserUseCase(uow=uow, password_hasher=StubPasswordHasher())

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(
            RegisterUserCommand(
                email='student@example.com',
                password='another-password',
            )
        )


@pytest.mark.asyncio
async def test_login_user_returns_access_token() -> None:
    uow = FakeUnitOfWork()
    user = User(
        id=uuid4(),
        email='admin@example.com',
        hashed_password='hashed::secret123',
        role=UserRole.ADMIN,
    )
    await uow.users.add(user)

    use_case = LoginUserUseCase(
        uow=uow,
        password_hasher=StubPasswordHasher(),
        token_service=StubTokenService(),
    )

    result = await use_case.execute(
        LoginUserCommand(
            email='admin@example.com',
            password='secret123',
        )
    )

    assert result.token_type == 'bearer'
    assert result.access_token.startswith('access-token-for-')
    assert result.refresh_token.startswith('refresh-token-')
    stored_session = uow.refresh_sessions.items[f'hash::{result.refresh_token}']
    assert stored_session.user_id == user.id
    assert stored_session.jti is not None
    assert uow.committed is True


@pytest.mark.asyncio
async def test_login_user_raises_error_when_email_is_unknown() -> None:
    use_case = LoginUserUseCase(
        uow=FakeUnitOfWork(),
        password_hasher=StubPasswordHasher(),
        token_service=StubTokenService(),
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            LoginUserCommand(
                email='missing@example.com',
                password='secret123',
            )
        )


@pytest.mark.asyncio
async def test_login_user_raises_error_when_password_is_invalid() -> None:
    uow = FakeUnitOfWork()
    user = User(
        id=uuid4(),
        email='admin@example.com',
        hashed_password='hashed::secret123',
        role=UserRole.ADMIN,
    )
    await uow.users.add(user)

    use_case = LoginUserUseCase(
        uow=uow,
        password_hasher=StubPasswordHasher(),
        token_service=StubTokenService(),
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(
            LoginUserCommand(
                email='admin@example.com',
                password='wrong-password',
            )
        )


@pytest.mark.asyncio
async def test_refresh_token_rotates_session_and_revokes_old_session() -> None:
    uow = FakeUnitOfWork()
    user = User(
        id=uuid4(),
        email='admin@example.com',
        hashed_password='hashed::secret123',
        role=UserRole.ADMIN,
    )
    await uow.users.add(user)
    old_session = RefreshSession(
        id=uuid4(),
        user_id=user.id,
        jti=uuid4(),
        token_hash='hash::refresh-token-old',
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_at=datetime.now(timezone.utc),
    )
    await uow.refresh_sessions.add(old_session)
    use_case = RefreshTokenUseCase(
        uow=uow,
        token_service=StubTokenService(),
    )

    result = await use_case.execute(
        RefreshTokenCommand(refresh_token='refresh-token-old')
    )

    assert result.access_token.startswith('access-token-for-')
    assert result.refresh_token.startswith('refresh-token-')
    assert uow.refresh_sessions.locked_token_hashes == ['hash::refresh-token-old']
    assert old_session.revoked_at is not None
    assert f'hash::{result.refresh_token}' in uow.refresh_sessions.items
    assert uow.committed is True


@pytest.mark.asyncio
async def test_refresh_token_rejects_revoked_session() -> None:
    uow = FakeUnitOfWork()
    user = User(
        id=uuid4(),
        email='admin@example.com',
        hashed_password='hashed::secret123',
        role=UserRole.ADMIN,
    )
    await uow.users.add(user)
    revoked_session = RefreshSession(
        id=uuid4(),
        user_id=user.id,
        jti=uuid4(),
        token_hash='hash::refresh-token-old',
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_at=datetime.now(timezone.utc),
        revoked_at=datetime.now(timezone.utc),
    )
    await uow.refresh_sessions.add(revoked_session)
    use_case = RefreshTokenUseCase(
        uow=uow,
        token_service=StubTokenService(),
    )

    with pytest.raises(InvalidRefreshTokenError):
        await use_case.execute(
            RefreshTokenCommand(refresh_token='refresh-token-old')
        )
