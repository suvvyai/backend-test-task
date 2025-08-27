import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.app import app
from core import settings
from core.database.client import get_mongo_client
from core.database.models import Channel, ChatBot
from core.database.registry import initialize_database


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
            f"Aborting tests: DB name '{settings.mongo.db_name}' does not end with 'test'.",
        )

    client = get_mongo_client()
    await client.drop_database(settings.mongo.db_name)

    await initialize_database()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient]:
    """Получить тестовый клиент"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def chat_bot() -> ChatBot:
    """Создание чат-бота после инициализации базы данных"""
    bot = ChatBot(name="Test Bot", secret_token="test_bot_token_123")
    await bot.insert()
    return bot


@pytest.fixture
async def channel(chat_bot: ChatBot) -> Channel:
    """Создание канала после инициализации базы данных"""
    channel = Channel(
        chat_bot_id=chat_bot.id,
        webhook_url="https://example.com/webhook",
        secret_token="channel_secret_123",
    )
    await channel.insert()
    return channel
