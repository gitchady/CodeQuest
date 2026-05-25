import pytest
from sqlalchemy import select

from app.infrastructure.database.models import ProgressModel, TaskAttemptModel


@pytest.mark.asyncio
async def test_task_flow_from_author_setup_to_student_progress(
    client,
    author_auth_headers,
    student_auth_headers,
    session_factory,
):
    course_response = await client.post(
        '/api/admin/courses',
        headers=author_auth_headers,
        json={
            'title': 'Tasks course',
            'description': 'Course with tasks.',
        },
    )
    course_id = course_response.json()['id']

    module_response = await client.post(
        f'/api/admin/courses/{course_id}/modules',
        headers=author_auth_headers,
        json={'title': 'HTTP', 'description': 'Practice', 'position': 1},
    )
    module_id = module_response.json()['id']

    section_response = await client.post(
        f'/api/admin/modules/{module_id}/sections',
        headers=author_auth_headers,
        json={'title': 'Basics', 'description': 'Intro', 'position': 1},
    )
    section_id = section_response.json()['id']

    task_response = await client.post(
        f'/api/admin/sections/{section_id}/tasks',
        headers=author_auth_headers,
        json={
            'title': 'HTTP method',
            'statement': 'Enter GET.',
            'position': 1,
            'check_type': 'exact_match',
            'expected_answer': 'GET',
            'accepted_answers': [],
            'answer_pattern': '',
            'max_attempts': 2,
            'reward_points': 3,
        },
    )
    task_id = task_response.json()['id']

    submit_response = await client.post(
        f'/api/learning/tasks/{task_id}/attempts',
        headers=student_auth_headers,
        json={'submitted_answer': 'GET'},
    )
    assert submit_response.status_code == 201

    async with session_factory() as session:
        attempts = (await session.execute(select(TaskAttemptModel))).scalars().all()
        progress_items = (await session.execute(select(ProgressModel))).scalars().all()

    assert len(attempts) == 1
    assert len(progress_items) == 1
    assert task_id in progress_items[0].completed_task_ids
    assert progress_items[0].total_points == 3