import asyncio
import math
import time

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.infrastructure.config.settings import RateLimitSettings


class InMemoryFixedWindowRateLimiter:
    def __init__(self, requests: int, window_seconds: int) -> None:
        self.requests = requests
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[float, int]] = {}
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> tuple[bool, int, int]:
        now = time.monotonic()
        async with self._lock:
            window_start, count = self._windows.get(key, (now, 0))
            elapsed = now - window_start
            if elapsed >= self.window_seconds:
                window_start = now
                count = 0

            retry_after = max(1, math.ceil(self.window_seconds - (now - window_start)))
            if count >= self.requests:
                return False, 0, retry_after

            count += 1
            self._windows[key] = (window_start, count)
            remaining = max(0, self.requests - count)
            return True, remaining, retry_after


def register_rate_limiting(
    app: FastAPI,
    settings: RateLimitSettings,
    api_prefix: str,
) -> None:
    app.state.rate_limit_settings = settings
    app.state.rate_limiter = InMemoryFixedWindowRateLimiter(
        requests=settings.requests,
        window_seconds=settings.window_seconds,
    )

    @app.middleware('http')
    async def rate_limit_middleware(request: Request, call_next) -> Response:
        current_settings: RateLimitSettings = app.state.rate_limit_settings
        if not current_settings.enabled or not request.url.path.startswith(api_prefix):
            return await call_next(request)

        limiter: InMemoryFixedWindowRateLimiter = app.state.rate_limiter
        client_host = request.client.host if request.client else 'unknown'
        allowed, remaining, retry_after = await limiter.check(client_host)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    'error': 'rate_limit_exceeded',
                    'message': 'Too many requests. Please retry later.',
                },
                headers={
                    'Retry-After': str(retry_after),
                    'X-RateLimit-Limit': str(current_settings.requests),
                    'X-RateLimit-Remaining': '0',
                },
            )

        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(current_settings.requests)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        return response
