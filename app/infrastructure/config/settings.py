from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseModel):
    title: str
    debug: bool
    prefix: str


class DatabaseSettings(BaseModel):
    url: str
    echo: bool


class JwtSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int


class CelerySettings(BaseModel):
    broker_url: str
    result_backend: str


class RateLimitSettings(BaseModel):
    enabled: bool
    requests: int
    window_seconds: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    environment: str = Field(default='development', validation_alias='APP_ENV')
    app_title: str = Field(default='FastAPI Education', validation_alias='APP_TITLE')
    app_debug: bool = Field(default=True, validation_alias='APP_DEBUG')
    api_prefix: str = Field(default='/api', validation_alias='API_PREFIX')
    database_url: str = Field(
        default='sqlite+aiosqlite:///./fastapi_education.db',
        validation_alias='DATABASE_URL',
    )
    database_echo: bool = Field(default=False, validation_alias='DATABASE_ECHO')
    jwt_secret_key: str = Field(validation_alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', validation_alias='JWT_ALGORITHM')
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        validation_alias='JWT_ACCESS_TOKEN_EXPIRE_MINUTES',
    )
    jwt_refresh_token_expire_minutes: int = Field(
        default=43200,
        validation_alias='JWT_REFRESH_TOKEN_EXPIRE_MINUTES',
    )
    celery_broker_url: str = Field(
        default='amqp://guest:guest@localhost:5672//',
        validation_alias='CELERY_BROKER_URL',
    )
    celery_result_backend: str = Field(
        default='redis://localhost:6379/1',
        validation_alias='CELERY_RESULT_BACKEND',
    )
    rate_limit_enabled: bool = Field(default=True, validation_alias='RATE_LIMIT_ENABLED')
    rate_limit_requests: int = Field(default=120, validation_alias='RATE_LIMIT_REQUESTS')
    rate_limit_window_seconds: int = Field(
        default=60,
        validation_alias='RATE_LIMIT_WINDOW_SECONDS',
    )

    @property
    def api(self) -> ApiSettings:
        return ApiSettings(
            title=self.app_title,
            debug=self.app_debug,
            prefix=self.api_prefix,
        )

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            url=self.database_url,
            echo=self.database_echo,
        )

    @property
    def jwt(self) -> JwtSettings:
        return JwtSettings(
            secret_key=self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
            access_token_expire_minutes=self.jwt_access_token_expire_minutes,
            refresh_token_expire_minutes=self.jwt_refresh_token_expire_minutes,
        )

    @property
    def celery(self) -> CelerySettings:
        return CelerySettings(
            broker_url=self.celery_broker_url,
            result_backend=self.celery_result_backend,
        )

    @property
    def rate_limit(self) -> RateLimitSettings:
        return RateLimitSettings(
            enabled=self.rate_limit_enabled,
            requests=self.rate_limit_requests,
            window_seconds=self.rate_limit_window_seconds,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
