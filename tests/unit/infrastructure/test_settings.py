from app.infrastructure.config.settings import Settings


def test_database_url_defaults_to_sqlite_when_not_configured() -> None:
    settings = Settings(_env_file=None, JWT_SECRET_KEY='test-secret')

    assert settings.database.url == 'sqlite+aiosqlite:///./fastapi_education.db'


def test_database_url_accepts_postgresql_asyncpg() -> None:
    database_url = 'postgresql+asyncpg://postgres:postgres@localhost:5432/perminof'

    settings = Settings(
        _env_file=None,
        DATABASE_URL=database_url,
        JWT_SECRET_KEY='test-secret',
    )

    assert settings.database.url == database_url


def test_requirements_include_postgresql_async_driver() -> None:
    requirements = {
        line.strip().split('[', maxsplit=1)[0].lower()
        for line in open('requirements.txt', encoding='utf-8')
        if line.strip()
    }

    assert 'asyncpg' in requirements


def test_env_example_prefers_postgresql_and_documents_sqlite_fallback() -> None:
    env_example = open('.env.example', encoding='utf-8').read()

    assert 'DATABASE_URL=postgresql+asyncpg://' in env_example
    assert 'sqlite+aiosqlite:///./fastapi_education.db' in env_example
