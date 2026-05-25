import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_student_can_submit_task_answer(
    client,
    student_auth_headers,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/learning/tasks/{seeded_tasks_tree.task_id}/attempts',
        headers=student_auth_headers,
        json={'submitted_answer': 'GET'},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload['status'] == 'correct'
    assert payload['awarded_points'] == 3


@pytest.mark.asyncio
async def test_student_can_create_code_submission(
    client,
    student_auth_headers,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'a, b = map(int, input().split())\nprint(a + b)'},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload['status'] == 'pending'
    assert payload['attempt_number'] == 1


@pytest.mark.asyncio
async def test_task_learning_endpoint_returns_401_without_token(
    client,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/learning/tasks/{seeded_tasks_tree.task_id}/attempts',
        json={'submitted_answer': 'GET'},
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload['error'] == 'authentication_error'


@pytest.mark.asyncio
async def test_code_submission_endpoint_returns_401_without_token(
    client,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/learning/code-tasks/{seeded_tasks_tree.code_task_id}/submissions',
        json={'source_code': 'print(1)'},
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload['error'] == 'authentication_error'


@pytest.mark.asyncio
async def test_submit_task_answer_returns_404_for_missing_task(
    client,
    student_auth_headers,
):
    response = await client.post(
        f'/api/learning/tasks/{uuid4()}/attempts',
        headers=student_auth_headers,
        json={'submitted_answer': 'GET'},
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload['error'] == 'task_not_found'


@pytest.mark.asyncio
async def test_submit_code_submission_returns_404_for_missing_code_task(
    client,
    student_auth_headers,
):
    response = await client.post(
        f'/api/learning/code-tasks/{uuid4()}/submissions',
        headers=student_auth_headers,
        json={'source_code': 'print(1)'},
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload['error'] == 'code_task_not_found'


@pytest.mark.asyncio
async def test_student_gets_403_on_author_task_endpoint(
    client,
    student_auth_headers,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/admin/sections/{seeded_tasks_tree.section_id}/tasks',
        headers=student_auth_headers,
        json={
            'title': 'Forbidden task',
            'statement': 'Should not be created.',
            'position': 10,
            'check_type': 'exact_match',
            'expected_answer': 'GET',
            'accepted_answers': [],
            'answer_pattern': '',
            'max_attempts': 2,
            'reward_points': 3,
        },
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload['error'] == 'permission_denied'


@pytest.mark.asyncio
async def test_student_gets_403_on_author_code_task_endpoint(
    client,
    student_auth_headers,
    seeded_tasks_tree,
):
    response = await client.post(
        f'/api/admin/sections/{seeded_tasks_tree.section_id}/code-tasks',
        headers=student_auth_headers,
        json={
            'title': 'Forbidden code task',
            'statement': 'Should not be created.',
            'position': 10,
            'language': 'python',
            'starter_code': 'print(1)',
            'max_attempts': 2,
            'reward_points': 5,
            'time_limit_seconds': 2,
            'memory_limit_mb': 128,
        },
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload['error'] == 'permission_denied'
