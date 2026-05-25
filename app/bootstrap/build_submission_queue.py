from functools import lru_cache

from redis.asyncio import Redis

from app.application.interfaces.submission_queue import SubmissionQueue
from app.infrastructure.config.settings import get_settings
from app.infrastructure.queues.redis_submission_queue import RedisSubmissionQueue


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url)


@lru_cache(maxsize=1)
def build_submission_queue() -> SubmissionQueue:
    settings = get_settings()
    return RedisSubmissionQueue(
        client=get_redis_client(),
        queue_name=settings.submission_queue_name,
    )