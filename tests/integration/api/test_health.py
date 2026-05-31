import pytest


@pytest.mark.asyncio
async def test_health_returns_liveness_payload(client):
    response = await client.get('/health')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['service'] == 'FastAPI Education'


@pytest.mark.asyncio
async def test_ready_checks_runtime_dependencies(client):
    response = await client.get('/ready')

    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['components']['database']['status'] == 'ok'
    assert payload['components']['celery']['status'] == 'ok'
