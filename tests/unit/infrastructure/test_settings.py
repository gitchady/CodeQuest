from app.infrastructure.config.settings import Settings


def _requirement_names() -> set[str]:
    names = set()
    for line in open('requirements.txt', encoding='utf-8'):
        requirement = line.strip()
        if not requirement or requirement.startswith('#'):
            continue
        name = requirement.split('==', maxsplit=1)[0].split('[', maxsplit=1)[0]
        names.add(name.lower())
    return names


def test_database_url_defaults_to_sqlite_when_not_configured() -> None:
    settings = Settings(_env_file=None, JWT_SECRET_KEY='test-secret')

    assert settings.database.url == 'sqlite+aiosqlite:///./fastapi_education.db'


def test_database_url_accepts_postgresql_asyncpg() -> None:
    database_url = 'postgresql+asyncpg://postgres:1234@localhost:5432/postgres'

    settings = Settings(
        _env_file=None,
        DATABASE_URL=database_url,
        JWT_SECRET_KEY='test-secret',
    )

    assert settings.database.url == database_url


def test_requirements_include_postgresql_async_driver() -> None:
    requirements = _requirement_names()

    assert 'asyncpg' in requirements


def test_requirements_include_celery_and_prometheus_client() -> None:
    requirements = _requirement_names()

    assert 'celery' in requirements
    assert 'prometheus-client' in requirements


def test_celery_defaults_use_rabbitmq_broker_and_redis_backend() -> None:
    settings = Settings(_env_file=None, JWT_SECRET_KEY='test-secret')

    assert settings.celery.broker_url == 'amqp://guest:guest@localhost:5672//'
    assert settings.celery.result_backend == 'redis://localhost:6379/1'


def test_jwt_refresh_token_ttl_defaults_to_30_days() -> None:
    settings = Settings(_env_file=None, JWT_SECRET_KEY='test-secret')

    assert settings.jwt.refresh_token_expire_minutes == 43200


def test_env_example_prefers_postgresql_and_documents_sqlite_fallback() -> None:
    env_example = open('.env.example', encoding='utf-8').read()

    assert 'DATABASE_URL=postgresql+asyncpg://' in env_example
    assert 'sqlite+aiosqlite:///./fastapi_education.db' in env_example


def test_env_example_documents_celery_rabbitmq_and_redis_backend() -> None:
    env_example = open('.env.example', encoding='utf-8').read()

    assert 'CELERY_BROKER_URL=amqp://' in env_example
    assert 'CELERY_RESULT_BACKEND=redis://' in env_example


def test_requirements_are_pinned() -> None:
    requirements = [
        line.strip()
        for line in open('requirements.txt', encoding='utf-8')
        if line.strip() and not line.startswith('#')
    ]

    assert all('==' in requirement for requirement in requirements)
