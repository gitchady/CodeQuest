import pytest

from conftest import ensure_safe_test_database_url


def test_allows_sqlite_test_database_without_extra_confirmation(monkeypatch) -> None:
    monkeypatch.delenv('ALLOW_TEST_DATABASE_DROP', raising=False)

    ensure_safe_test_database_url('sqlite+aiosqlite:////tmp/test_fastapi.db')


def test_allows_postgres_database_with_test_name(monkeypatch) -> None:
    monkeypatch.delenv('ALLOW_TEST_DATABASE_DROP', raising=False)

    ensure_safe_test_database_url(
        'postgresql+asyncpg://perminof:perminof@localhost:5432/perminof_test'
    )


def test_rejects_non_test_external_database_without_confirmation(monkeypatch) -> None:
    monkeypatch.delenv('ALLOW_TEST_DATABASE_DROP', raising=False)

    with pytest.raises(RuntimeError, match='Refusing to drop database schema'):
        ensure_safe_test_database_url(
            'postgresql+asyncpg://perminof:perminof@localhost:5432/perminof'
        )


def test_allows_non_test_external_database_with_explicit_confirmation(monkeypatch) -> None:
    monkeypatch.setenv('ALLOW_TEST_DATABASE_DROP', '1')

    ensure_safe_test_database_url(
        'postgresql+asyncpg://perminof:perminof@localhost:5432/perminof'
    )
