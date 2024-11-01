from datetime import timedelta
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.future import select
from db.models.post import Post
from main import app
from db.db_settings import Base
from db.models.user import User
from utils.auth import create_access_token
from utils.settings import DB_HOST, DB_USERNAME, DB_PASSWORD, DB_PORT, DB_DRIVER, DB_DATABASE

TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestAsyncSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="module")
async def db():
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
async def test_user(db: AsyncSession):
    username = "testuser"
    email = "testuser@example.com"
    password = "testpassword"

    # Перевірка, чи існує користувач
    existing_user_query = await db.execute(select(User).where(User.username == username))
    existing_user = existing_user_query.scalar_one_or_none()

    if existing_user is None:
        # Якщо користувача не існує, створюємо нового
        user = User(username=username, email=email, password=password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user = existing_user

    token_expires = timedelta(minutes=30)  # або інший час
    token = create_access_token(data={"sub": user.username}, expires_delta=token_expires)

    # Додаємо id користувача до user_data
    user_data = {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "token": token,
        "id": user.id
    }

    return user_data


@pytest.fixture(scope="module")
async def test_post(db: AsyncSession, test_user):
    post_data = {
        "title": "Test Post",
        "content": "This is a test post.",
        "autoreply": True,
        "autoreply_delay": 5,
        "autoreply_msg": "This is an autoreply message."
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/posts/", json=post_data, headers={"Authorization": f"Bearer {test_user['token']}"})
        assert response.status_code == status.HTTP_201_CREATED
        post = response.json()
        print("Created post ID:", post["id"])  # Додайте це

    return post
