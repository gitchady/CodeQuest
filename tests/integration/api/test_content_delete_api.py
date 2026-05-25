from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_delete_lecture_returns_204_and_removes_lecture(
    client,
    admin_auth_headers,
    seeded_course_tree,
):
    response = await client.delete(
        f"/api/admin/lectures/{seeded_course_tree.lecture_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    lecture_response = await client.get(f"/api/lectures/{seeded_course_tree.lecture_id}")
    assert lecture_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_module_removes_subtree_from_public_structure(
    client,
    admin_auth_headers,
    seeded_course_tree,
):
    response = await client.delete(
        f"/api/admin/modules/{seeded_course_tree.module_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    structure_response = await client.get(
        f"/api/courses/{seeded_course_tree.course_id}/structure"
    )
    assert structure_response.status_code == 200
    assert structure_response.json()["modules"] == []


@pytest.mark.asyncio
async def test_delete_course_removes_course_from_public_list(
    client,
    admin_auth_headers,
    seeded_course_tree,
):
    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 204

    courses_response = await client.get("/api/courses")
    assert courses_response.status_code == 200
    assert courses_response.json() == []


@pytest.mark.asyncio
async def test_delete_section_returns_404_when_section_is_missing(
    client,
    admin_auth_headers,
):
    response = await client.delete(
        f"/api/admin/sections/{uuid4()}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "section_not_found"


@pytest.mark.asyncio
async def test_delete_route_returns_401_without_token(client, seeded_course_tree):
    response = await client.delete(f"/api/admin/courses/{seeded_course_tree.course_id}")

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"] == "authentication_error"


@pytest.mark.asyncio
async def test_delete_route_returns_403_for_student(
    client,
    student_auth_headers,
    seeded_course_tree,
):
    response = await client.delete(
        f"/api/admin/courses/{seeded_course_tree.course_id}",
        headers=student_auth_headers,
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"] == "permission_denied"
