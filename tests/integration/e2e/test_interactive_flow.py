import pytest
from sqlalchemy import select

from app.infrastructure.database.models import ProgressModel, QuestionAttemptModel


@pytest.mark.asyncio
async def test_interactive_flow_from_author_setup_to_student_progress(
    client,
    author_auth_headers,
    student_auth_headers,
    session_factory,
):
    course_response = await client.post(
        '/api/admin/courses',
        headers=author_auth_headers,
        json={
            'title': 'Interactive FastAPI',
            'description': 'Course with questions inside sections.',
        },
    )
    course_id = course_response.json()['id']

    module_response = await client.post(
        f'/api/admin/courses/{course_id}/modules',
        headers=author_auth_headers,
        json={'title': 'HTTP', 'description': 'Methods', 'position': 1},
    )
    module_id = module_response.json()['id']

    section_response = await client.post(
        f'/api/admin/modules/{module_id}/sections',
        headers=author_auth_headers,
        json={'title': 'Basics', 'description': 'Intro', 'position': 1},
    )
    section_id = section_response.json()['id']

    question_response = await client.post(
        f'/api/admin/sections/{section_id}/questions',
        headers=author_auth_headers,
        json={
            'text': 'Which method reads a resource?',
            'position': 1,
            'question_type': 'single_choice',
            'max_attempts': 2,
            'reward_points': 5,
        },
    )
    question_id = question_response.json()['id']

    await client.post(
        f'/api/admin/questions/{question_id}/answer-options',
        headers=author_auth_headers,
        json={'text': 'POST', 'position': 1, 'is_correct': False},
    )
    correct_option_response = await client.post(
        f'/api/admin/questions/{question_id}/answer-options',
        headers=author_auth_headers,
        json={'text': 'GET', 'position': 2, 'is_correct': True},
    )
    correct_option_id = correct_option_response.json()['id']

    start_response = await client.get(
        f'/api/learning/questions/{question_id}/attempt',
        headers=student_auth_headers,
    )
    assert start_response.status_code == 200

    submit_response = await client.post(
        f'/api/learning/questions/{question_id}/attempts',
        headers=student_auth_headers,
        json={'selected_option_ids': [correct_option_id]},
    )
    assert submit_response.status_code == 201

    async with session_factory() as session:
        attempts = (await session.execute(select(QuestionAttemptModel))).scalars().all()
        progress_items = (await session.execute(select(ProgressModel))).scalars().all()

    assert len(attempts) == 1
    assert len(progress_items) == 1
    assert progress_items[0].total_points == 5