from fastapi import APIRouter, Depends, status

from app.application.dto.auth_token import AuthToken
from app.application.use_cases.auth.login_user import LoginUserCommand, LoginUserUseCase
from app.application.use_cases.auth.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)
from app.domain.entities.user import User
from app.infrastructure.database import SqlAlchemyUnitOfWork
from app.infrastructure.security.jwt_token_service import InvalidTokenError

from app.presentation.api.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
    get_token_service,
    get_uow,
)
from app.presentation.api.schemas import (
    CurrentUserResponse,
    ErrorResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisteredUserResponse,
    RegisterUserRequest,
    TokenResponse,
)
from app.presentation.exceptions import AuthenticationError
from app.application.interfaces.services.token_service import TokenService

router = APIRouter(prefix='/auth', tags=['Auth'])


def _to_token_response(result: AuthToken) -> TokenResponse:
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post(
    '/register',
    response_model=RegisteredUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Register new user',
    description=(
        'Creates a new user account in the system. '
        'A public registration always creates a user with the student role.'
    ),
    responses={
        400: {
            'description': 'Domain or application validation error.',
            'model': ErrorResponse,
        },
    },
)
async def register_user(
    request: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> RegisteredUserResponse:
    result = await use_case.execute(
        RegisterUserCommand(
            email=request.email,
            password=request.password,
        )
    )
    return RegisteredUserResponse.model_validate(result)


@router.post(
    '/login',
    response_model=TokenResponse,
    summary='Login user',
    description=(
        'Authenticates a user by email and password and returns a JWT access token.'
    ),
    responses={
        400: {
            'description': 'Invalid email or password.',
            'model': ErrorResponse,
        },
    },
)
async def login_user(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> TokenResponse:
    result = await use_case.execute(
        LoginUserCommand(
            email=request.email,
            password=request.password,
        )
    )
    return _to_token_response(result)


@router.post(
    '/refresh',
    response_model=TokenResponse,
    summary='Refresh access token',
    description='Issues a new access token from a valid refresh token.',
    responses={
        401: {
            'description': 'Refresh token is missing, invalid or expired.',
            'model': ErrorResponse,
        },
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
    try:
        user_id = token_service.get_refresh_user_id(request.refresh_token)
    except InvalidTokenError as exc:
        raise AuthenticationError(str(exc)) from exc

    user = await uow.users.get_by_id(user_id)
    if user is None:
        raise AuthenticationError('User from token was not found.')

    result = AuthToken(
        access_token=token_service.create_access_token(
            user_id=user.id,
            role=user.role.value,
        ),
        refresh_token=token_service.create_refresh_token(
            user_id=user.id,
            role=user.role.value,
        ),
    )
    return _to_token_response(result)



@router.get(
    '/me',
    response_model=CurrentUserResponse,
    summary='Get current user',
    description='Returns the currently authenticated user resolved from Bearer token.',
    responses={
        401: {
            'description': 'Authentication credentials are missing or invalid.',
            'model': ErrorResponse,
        },
    },
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)
