import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from main import app


@pytest.mark.anyio
async def test_create_post(db: AsyncSession, test_user):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        post_data = {
            "title": "Test Post",
            "content": "This is a test post.",
            "owner_id": test_user["id"],
        }
        response = await ac.post("/posts/", json=post_data, headers={"Authorization": f"Bearer {test_user['token']}"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["owner_id"] == test_user["id"]

@pytest.mark.anyio
async def test_read_post(db: AsyncSession, test_user, test_post):
    print("Expected post ID:", test_post["id"])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/posts/{test_post['id']}", headers={"Authorization": f"Bearer {test_user['token']}"})
        print(f"Response: {response.json()}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == test_post["id"]

@pytest.mark.anyio
async def test_read_posts(db: AsyncSession, test_user):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/posts/", headers={"Authorization": f"Bearer {test_user['token']}"})

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_update_post(db: AsyncSession, test_user, test_post):
    update_data = {"title": "Updated Post"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/posts/{test_post['id']}", json=update_data,
                                headers={"Authorization": f"Bearer {test_user['token']}"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_data["title"]


@pytest.mark.anyio
async def test_update_non_existent_post(db: AsyncSession, test_user):
    update_data = {"title": "Non Existent Post"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/posts/999999", json=update_data,
                                headers={"Authorization": f"Bearer {test_user['token']}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_post(db: AsyncSession, test_user, test_post):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/posts/{test_post['id']}", headers={"Authorization": f"Bearer {test_user['token']}"})
        assert response.status_code == status.HTTP_200_OK

        delete_response = await ac.delete(f"/posts/{test_post['id']}",
                                          headers={"Authorization": f"Bearer {test_user['token']}"})
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT