from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_answer_option_returns_204_when_question_stays_valid(
    client,
    author_auth_headers,
    seeded_interactive_tree,
):
    extra_option_response = await client.post(
        f"/api/admin/questions/{seeded_interactive_tree.question_id}/answer-options",
        headers=author_auth_headers,
        json={'text': 'PATCH', 'position': 3, 'is_correct': False},
    )
    extra_option_id = extra_option_response.json()['id']

    response = await client.delete(
        f"/api/admin/answer-options/{extra_option_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_question_returns_204_and_removes_question_from_public_structure(
    client,
    author_auth_headers,
    seeded_interactive_tree,
):
    response = await client.delete(
        f"/api/admin/questions/{seeded_interactive_tree.question_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 204

    structure_response = await client.get(
        f"/api/courses/{seeded_interactive_tree.course_id}/structure"
    )
    assert structure_response.status_code == 200
    section = structure_response.json()['modules'][0]['sections'][0]
    assert section['question_ids'] == []


@pytest.mark.asyncio
async def test_delete_question_returns_400_after_student_attempt(
    client,
    author_auth_headers,
    student_auth_headers,
    seeded_interactive_tree,
):
    submit_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={'selected_option_ids': [seeded_interactive_tree.correct_option_id]},
    )
    assert submit_response.status_code == 201

    response = await client.delete(
        f"/api/admin/questions/{seeded_interactive_tree.question_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload['error'] == 'application_error'


@pytest.mark.asyncio
async def test_delete_answer_option_returns_400_when_question_would_become_invalid(
    client,
    author_auth_headers,
    seeded_interactive_tree,
):
    response = await client.delete(
        f"/api/admin/answer-options/{seeded_interactive_tree.wrong_option_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload['error'] == 'domain_error'


@pytest.mark.asyncio
async def test_delete_answer_option_returns_400_after_student_attempt(
    client,
    author_auth_headers,
    student_auth_headers,
    seeded_interactive_tree,
):
    submit_response = await client.post(
        f"/api/learning/questions/{seeded_interactive_tree.question_id}/attempts",
        headers=student_auth_headers,
        json={'selected_option_ids': [seeded_interactive_tree.correct_option_id]},
    )
    assert submit_response.status_code == 201

    response = await client.delete(
        f"/api/admin/answer-options/{seeded_interactive_tree.wrong_option_id}",
        headers=author_auth_headers,
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload['error'] == 'application_error'


@pytest.mark.asyncio
async def test_delete_question_returns_404_when_question_is_missing(
    client,
    author_auth_headers,
):
    response = await client.delete(
        f"/api/admin/questions/{uuid4()}",
        headers=author_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()['error'] == 'question_not_found'
