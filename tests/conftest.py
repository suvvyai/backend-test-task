import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient


from src.app.app import app
from src.core import settings
from src.core.database.client import get_mongo_client
from src.core.database.registry import initialize_database


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope="function")
async def setup_database() -> None:
    """
    Подготавливает чистую и инициализированную БД перед каждым тестом.
    """
    if not settings.mongo.db_name.lower().endswith("test"):
        raise RuntimeError(
            f"Aborting tests: DB name '{settings.mongo.db_name}' does not end with 'test'."
        )

    client = get_mongo_client()
    await client.drop_database(settings.mongo.db_name)

    await initialize_database()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Получить тестовый клиент"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
