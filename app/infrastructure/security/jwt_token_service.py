from datetime import datetime, timedelta, timezone
from uuid import uuid4
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError as JwtInvalidTokenError

from app.application.interfaces.services.token_service import TokenService
from app.infrastructure.config import get_settings


class InvalidTokenError(Exception):
    pass


class JwtTokenService(TokenService):
    def __init__(self) -> None:
        settings = get_settings()
        self.secret_key = settings.jwt.secret_key
        self.algorithm = settings.jwt.algorithm
        self.access_token_expire_minutes = settings.jwt.access_token_expire_minutes
        self.refresh_token_expire_minutes = settings.jwt.refresh_token_expire_minutes

    def create_access_token(self, user_id: UUID, role: str) -> str:
        return self._create_token(
            user_id=user_id,
            role=role,
            token_type='access',
            minutes=self.access_token_expire_minutes,
        )

    def create_refresh_token(self, user_id: UUID, role: str) -> str:
        return self._create_token(
            user_id=user_id,
            role=role,
            token_type='refresh',
            minutes=self.refresh_token_expire_minutes,
        )

    def _create_token(self, user_id: UUID, role: str, token_type: str, minutes: int) -> str:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=minutes)
        payload = {
            'sub': str(user_id),
            'role': role,
            'typ': token_type,
            'iat': issued_at,
            'exp': expires_at,
            'jti': str(uuid4()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def get_user_id(self, token: str) -> UUID:
        return self._get_user_id(token=token, expected_type='access')

    def get_refresh_user_id(self, token: str) -> UUID:
        return self._get_user_id(token=token, expected_type='refresh')

    def _get_user_id(self, token: str, expected_type: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'require': ['sub', 'exp', 'typ']},
            )
        except (JwtInvalidTokenError, ValueError) as exc:
            raise InvalidTokenError('Token is invalid or expired.') from exc

        token_type = payload.get('typ')
        if token_type != expected_type:
            raise InvalidTokenError('Token type is invalid.')

        subject = payload.get('sub')
        if subject is None:
            raise InvalidTokenError('Token does not contain subject.')

        try:
            return UUID(subject)
        except ValueError as exc:
            raise InvalidTokenError('Token subject is invalid.') from exc
