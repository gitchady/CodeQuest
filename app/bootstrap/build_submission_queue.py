from functools import lru_cache

from app.application.interfaces.submission_queue import SubmissionQueue
from app.infrastructure.queues.celery_submission_queue import CelerySubmissionQueue


@lru_cache(maxsize=1)
def build_submission_queue() -> SubmissionQueue:
    from app.infrastructure.workers.code_submission_tasks import (
        process_code_submission_task,
    )

    return CelerySubmissionQueue(task=process_code_submission_task)
