import pytest


@pytest.mark.asyncio
async def test_get_task_returns_public_task_details(client, seeded_tasks_tree):
    response = await client.get(f'/api/tasks/{seeded_tasks_tree.task_id}')

    assert response.status_code == 200
    payload = response.json()
    assert payload['id'] == seeded_tasks_tree.task_id
    assert payload['title'] == 'HTTP method'
    assert 'expected_answer' not in payload
    assert 'accepted_answers' not in payload
    assert 'answer_pattern' not in payload


@pytest.mark.asyncio
async def test_get_code_task_returns_editor_configuration_only(client, seeded_tasks_tree):
    response = await client.get(f'/api/code-tasks/{seeded_tasks_tree.code_task_id}')

    assert response.status_code == 200
    payload = response.json()
    assert payload['id'] == seeded_tasks_tree.code_task_id
    assert payload['language'] == 'python'
    assert 'starter_code' in payload


@pytest.mark.asyncio
async def test_get_course_structure_returns_tasks_and_code_tasks(client, seeded_tasks_tree):
    response = await client.get(f'/api/courses/{seeded_tasks_tree.course_id}/structure')

    assert response.status_code == 200
    payload = response.json()
    section = payload['modules'][0]['sections'][0]
    assert seeded_tasks_tree.task_id in section['task_ids']
    assert seeded_tasks_tree.code_task_id in section['code_task_ids']
    assert any(item['id'] == seeded_tasks_tree.task_id for item in section['tasks'])
    assert any(item['id'] == seeded_tasks_tree.code_task_id for item in section['code_tasks'])