from celery import Celery  # type: ignore[import-untyped]

from app.infrastructure.config.settings import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    celery_app = Celery(
        'perminof',
        broker=settings.celery.broker_url,
        backend=settings.celery.result_backend,
        include=['app.infrastructure.workers.code_submission_tasks'],
    )
    celery_app.conf.update(
        accept_content=['json'],
        result_serializer='json',
        task_serializer='json',
        task_track_started=True,
        timezone='UTC',
    )
    return celery_app


celery_app = create_celery_app()
