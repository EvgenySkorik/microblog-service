import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from microblog.core.database import get_db
from microblog.db.base import Base
from microblog.db.models import User

TEST_USER_1 = {"id": 1, "name": "Oliver", "api_key": "000"}
TEST_USER_2 = {"id": 2, "name": "Jenia", "api_key": "123"}
TEST_USER_3 = {"id": 3, "name": "Kate", "api_key": "222"}


@pytest.fixture(scope="session")
def app():
    """Экземпляр FastAPI для тестов без lifespan"""
    _app: FastAPI = FastAPI(title="Test APP")

    from microblog.api.routes import (
        medias_router,
        start_router,
        tweets_router,
        users_router,
    )

    _app.include_router(start_router)
    _app.include_router(users_router)
    _app.include_router(tweets_router)
    _app.include_router(medias_router)

    return _app


@pytest.fixture(scope="session")
def setup_database(app):
    """Создание движка и таблиц БД для тестов"""
    _engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async def init_tables():
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_tables())

    TestingSessionLocal = async_sessionmaker(
        _engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    async def create_test_users():
        async with TestingSessionLocal() as session:
            user1 = User(**TEST_USER_1)
            user2 = User(**TEST_USER_2)
            user3 = User(**TEST_USER_3)
            session.add_all([user1, user2, user3])
            await session.commit()

    asyncio.run(create_test_users())

    app.dependency_overrides[get_db] = override_get_db  # type: ignore

    return _engine


@pytest.fixture
def client(app: FastAPI, setup_database):
    """Клиент для тестов"""
    with TestClient(app) as client:
        yield client
