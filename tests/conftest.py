import sys
from pathlib import Path
import asyncio

# Добавляем src в PYTHONPATH для тестов
ROOT = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(ROOT))

import pytest
import motor.motor_asyncio
from httpx import AsyncClient, ASGITransport

# Импорты приложения
from core import settings
from core.database.registry import initialize_database
from app.app import app


@pytest.fixture
def event_loop():
    """Создаём новый event loop для каждого теста"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def init_db():
    """Инициализировать базу данных перед тестом"""
    await initialize_database()
    yield


@pytest.fixture(autouse=True)
async def drop_db():
    """Удалять тестовую БД перед каждым тестом"""
    if not settings.mongo.db_name.lower().endswith("test"):
        raise RuntimeError("Опасное имя БД, ожидается тестовая БД")
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo.url)
    await client.drop_database(settings.mongo.db_name)
    yield


@pytest.fixture
async def client():
    """Асинхронный HTTP-клиент для тестов"""
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
    ) as c:
        yield c
