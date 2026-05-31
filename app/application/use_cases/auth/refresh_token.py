from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.application.dto.auth_token import AuthToken
from app.application.exceptions import InvalidRefreshTokenError
from app.application.interfaces.services.token_service import TokenService
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.entities.refresh_session import RefreshSession


@dataclass(slots=True)
class RefreshTokenCommand:
    refresh_token: str


class RefreshTokenUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        token_service: TokenService,
    ) -> None:
        self.uow = uow
        self.token_service = token_service

    async def execute(self, command: RefreshTokenCommand) -> AuthToken:
        token_hash = self.token_service.hash_refresh_token(command.refresh_token)
        now = datetime.now(timezone.utc)

        async with self.uow:
            refresh_session = (
                await self.uow.refresh_sessions.get_by_token_hash_for_update(
                    token_hash
                )
            )
            if refresh_session is None or not refresh_session.is_active(now):
                raise InvalidRefreshTokenError('Refresh token is invalid or expired.')

            user = await self.uow.users.get_by_id(refresh_session.user_id)
            if user is None:
                raise InvalidRefreshTokenError('Refresh token user was not found.')

            refresh_session.revoke(now)
            await self.uow.refresh_sessions.save(refresh_session)

            new_refresh_token = self.token_service.create_refresh_token()
            await self.uow.refresh_sessions.add(
                RefreshSession(
                    id=uuid4(),
                    user_id=user.id,
                    jti=uuid4(),
                    token_hash=self.token_service.hash_refresh_token(
                        new_refresh_token
                    ),
                    expires_at=self.token_service.get_refresh_token_expires_at(),
                    created_at=now,
                )
            )
            access_token = self.token_service.create_access_token(
                user_id=user.id,
                role=user.role.value,
            )
            await self.uow.commit()
            return AuthToken(
                access_token=access_token,
                refresh_token=new_refresh_token,
            )
