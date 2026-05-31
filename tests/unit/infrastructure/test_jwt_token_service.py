from uuid import uuid4

import jwt
import pytest

from app.infrastructure.security.jwt_token_service import InvalidTokenError, JwtTokenService


def test_jwt_service_issues_and_decodes_access_token() -> None:
    service = JwtTokenService()
    user_id = uuid4()

    token = service.create_access_token(user_id=user_id, role='student')

    assert service.get_user_id(token) == user_id


def test_jwt_service_issues_and_decodes_refresh_token() -> None:
    service = JwtTokenService()
    user_id = uuid4()

    token = service.create_refresh_token(user_id=user_id, role='student')

    assert service.get_refresh_user_id(token) == user_id


def test_jwt_service_rejects_refresh_token_as_access_token() -> None:
    service = JwtTokenService()
    token = service.create_refresh_token(user_id=uuid4(), role='student')

    with pytest.raises(InvalidTokenError):
        service.get_user_id(token)


def test_jwt_service_requires_exp_claim() -> None:
    service = JwtTokenService()
    token = jwt.encode(
        {'sub': str(uuid4()), 'typ': 'access'},
        service.secret_key,
        algorithm=service.algorithm,
    )

    with pytest.raises(InvalidTokenError):
        service.get_user_id(token)


def test_jwt_service_rejects_invalid_subject() -> None:
    service = JwtTokenService()
    token = jwt.encode(
        {'sub': 'not-a-uuid', 'typ': 'access', 'exp': 4102444800},
        service.secret_key,
        algorithm=service.algorithm,
    )

    with pytest.raises(InvalidTokenError):
        service.get_user_id(token)
