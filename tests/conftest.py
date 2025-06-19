import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator

import motor.motor_asyncio
import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient

load_dotenv("../.env")

from core import settings
from core.database import initialize_database
from core.database.models import ChatBot, Dialogue
from core.database.models.channel import Channel
from src.app.app import app


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    """Ивент луп"""
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope="session")
async def init_db() -> None:
    """Ининциализировать базу данных"""
    await initialize_database()


@pytest.fixture(autouse=True)
async def drop_db() -> None:
    """Дропнуть бд перед каждым тестом"""
    if not settings.mongo.db_name.lower().endswith("test"):
        raise RuntimeError

    mongo: motor.motor_asyncio.AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo.url)
    await mongo.drop_database(settings.mongo.db_name)


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient]:
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            yield client


@pytest.fixture(scope="function")
async def chat_bot() -> ChatBot:
    bot = ChatBot(name="Test Bot", secret_token="test-token")
    await bot.insert()
    return bot


@pytest.fixture(scope="function")
async def dialogue(chat_bot: ChatBot) -> Dialogue:
    dialogue = Dialogue(
        chat_bot_id=chat_bot.id,
        chat_id="test_chat",
    )
    await dialogue.insert()
    return dialogue


@pytest.fixture(scope="function")
async def channel(client, chat_bot: ChatBot) -> Channel:
    channel = Channel(
        chat_bot_id=chat_bot.id,
        chat_id="test_chat",
        response_url="http://example.com",
        response_token="channel_token",
    )
    await channel.insert()
    return channel
