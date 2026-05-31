import pytest

from app.infrastructure.config.settings import RateLimitSettings
from app.infrastructure.rate_limiting import InMemoryFixedWindowRateLimiter


@pytest.mark.asyncio
async def test_api_rate_limit_returns_429_after_limit(client, app):
    app.state.rate_limit_settings = RateLimitSettings(
        enabled=True,
        requests=2,
        window_seconds=60,
    )
    app.state.rate_limiter = InMemoryFixedWindowRateLimiter(
        requests=2,
        window_seconds=60,
    )

    first_response = await client.get('/api/courses')
    second_response = await client.get('/api/courses')
    limited_response = await client.get('/api/courses')

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert limited_response.status_code == 429
    assert limited_response.json() == {
        'error': 'rate_limit_exceeded',
        'message': 'Too many requests. Please retry later.',
    }
    assert limited_response.headers['Retry-After'] == '60'
    assert limited_response.headers['X-RateLimit-Limit'] == '2'
    assert limited_response.headers['X-RateLimit-Remaining'] == '0'


@pytest.mark.asyncio
async def test_rate_limit_can_be_disabled(client, app):
    app.state.rate_limit_settings = RateLimitSettings(
        enabled=False,
        requests=1,
        window_seconds=60,
    )
    app.state.rate_limiter = InMemoryFixedWindowRateLimiter(
        requests=1,
        window_seconds=60,
    )

    first_response = await client.get('/api/courses')
    second_response = await client.get('/api/courses')

    assert first_response.status_code == 200
    assert second_response.status_code == 200
