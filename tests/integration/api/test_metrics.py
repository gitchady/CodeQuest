import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_prometheus_payload() -> None:
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.get('/metrics')

    assert response.status_code == 200
    assert 'python_info' in response.text
