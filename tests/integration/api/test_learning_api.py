import pytest


@pytest.mark.asyncio
async def test_get_question_attempt_returns_question_state(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    response = await client.get(
        f'/api/learning/questions/{seeded_interactive_tree.question_id}/attempt',
        headers=student_auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['question_id'] == seeded_interactive_tree.question_id
    assert payload['can_submit'] is True
    assert payload['is_solved'] is False
    assert len(payload['answer_options']) == 2


@pytest.mark.asyncio
async def test_submit_question_answer_returns_created_attempt(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    response = await client.post(
        f'/api/learning/questions/{seeded_interactive_tree.question_id}/attempts',
        headers=student_auth_headers,
        json={'selected_option_ids': [seeded_interactive_tree.correct_option_id]},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload['result_status'] == 'correct'
    assert payload['awarded_points'] == 5
    assert payload['selected_option_ids'] == [seeded_interactive_tree.correct_option_id]


@pytest.mark.asyncio
async def test_get_question_attempt_result_returns_previous_attempt(
    client,
    student_auth_headers,
    seeded_interactive_tree,
):
    submit_response = await client.post(
        f'/api/learning/questions/{seeded_interactive_tree.question_id}/attempts',
        headers=student_auth_headers,
        json={'selected_option_ids': [seeded_interactive_tree.correct_option_id]},
    )
    attempt_id = submit_response.json()['attempt_id']

    result_response = await client.get(
        f'/api/learning/attempts/{attempt_id}/result',
        headers=student_auth_headers,
    )

    assert result_response.status_code == 200
    assert result_response.json()['attempt_id'] == attempt_id


@pytest.mark.asyncio
async def test_foreign_author_cannot_update_question(
    client,
    other_author_auth_headers,
    seeded_interactive_tree,
):
    response = await client.put(
        f'/api/admin/questions/{seeded_interactive_tree.question_id}',
        headers=other_author_auth_headers,
        json={
            'text': 'Changed foreign question',
            'position': 1,
            'question_type': 'single_choice',
            'max_attempts': 2,
            'reward_points': 5,
        },
    )

    assert response.status_code == 403
    assert response.json()['error'] == 'permission_denied'