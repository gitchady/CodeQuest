from typing import Any

from celery import Celery  # type: ignore[import-untyped]
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.infrastructure.celery_app import celery_app
from app.infrastructure.config import get_settings
from app.infrastructure.database import SessionFactory

router = APIRouter(tags=['Health'])


def _configured_status(value: str) -> dict[str, str]:
    return {'status': 'ok' if value else 'error'}


async def _check_database() -> dict[str, str]:
    try:
        async with SessionFactory() as session:
            await session.execute(text('SELECT 1'))
    except Exception as exc:
        return {'status': 'error', 'detail': exc.__class__.__name__}
    return {'status': 'ok'}


def _check_celery(app: Celery) -> dict[str, str]:
    broker_url = str(app.conf.broker_url or '')
    result_backend = str(app.conf.result_backend or '')
    if not broker_url or not result_backend:
        return {'status': 'error', 'detail': 'celery broker or result backend is not configured'}
    return {'status': 'ok'}


@router.get('/health', include_in_schema=False)
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        'status': 'ok',
        'environment': settings.environment,
        'service': settings.api.title,
    }


@router.get('/ready', include_in_schema=False)
async def ready(response: Response) -> dict[str, Any]:
    settings = get_settings()
    components: dict[str, dict[str, str]] = {
        'database': await _check_database(),
        'celery': _check_celery(celery_app),
        'broker_url': _configured_status(settings.celery.broker_url),
        'result_backend': _configured_status(settings.celery.result_backend),
    }
    is_ready = all(component['status'] == 'ok' for component in components.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        'status': 'ok' if is_ready else 'error',
        'components': components,
    }
