import asyncio
from uuid import UUID

from app.application.exceptions import RetryableExecutionError
from app.bootstrap.build_code_submission_worker import (
    build_process_code_submission_use_case,
)
from app.infrastructure.celery_app import celery_app
from app.infrastructure.workers.code_submission_worker import process_code_submission


@celery_app.task(
    bind=True,
    name='code_submissions.process',
    autoretry_for=(RetryableExecutionError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 3},
)
def process_code_submission_task(self, submission_id: str) -> None:
    process_use_case = build_process_code_submission_use_case()
    asyncio.run(
        process_code_submission(
            submission_id=UUID(submission_id),
            process_use_case=process_use_case,
        )
    )
