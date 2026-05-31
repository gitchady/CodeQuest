from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.application.dto.auth_token import AuthToken
from app.application.exceptions import InvalidCredentialsError
from app.application.interfaces.services.password_hasher import PasswordHasher
from app.application.interfaces.services.token_service import TokenService
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.refresh_session import RefreshSession


@dataclass(slots=True)
class LoginUserCommand:
    email: str
    password: str


class LoginUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self.uow = uow
        self.password_hasher = password_hasher
        self.token_service = token_service

    async def execute(self, command: LoginUserCommand) -> AuthToken:
        async with self.uow:
            user = await self.uow.users.get_by_email(command.email)
            if user is None:
                raise InvalidCredentialsError('Invalid email or password.')

            is_valid_password = self.password_hasher.verify(
                command.password,
                user.hashed_password,
            )
            if not is_valid_password:
                raise InvalidCredentialsError('Invalid email or password.')

            access_token = self.token_service.create_access_token(
                user_id=user.id,
                role=user.role.value,
            )
            refresh_token = self.token_service.create_refresh_token()
            await self.uow.refresh_sessions.add(
                RefreshSession(
                    id=uuid4(),
                    user_id=user.id,
                    jti=uuid4(),
                    token_hash=self.token_service.hash_refresh_token(refresh_token),
                    expires_at=self.token_service.get_refresh_token_expires_at(),
                    created_at=datetime.now(timezone.utc),
                )
            )
            await self.uow.commit()
            return AuthToken(access_token=access_token, refresh_token=refresh_token)
