import pytest


@pytest.mark.asyncio
async def test_frontend_index_is_served(client):
    response = await client.get('/')

    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert '<title>Perminof</title>' in response.text
    assert 'Content composer' in response.text


@pytest.mark.asyncio
async def test_frontend_static_assets_are_served(client):
    response = await client.get('/static/app.js')

    assert response.status_code == 200
    assert 'loadCourses' in response.text
