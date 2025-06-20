from contextlib import asynccontextmanager

from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from core.database.models.chat_bot import ChatBot
from core.database.models.channel import Channel
from core.database.models.dialogue import Dialogue
from core.settings_model import settings
from app.routers.api import api_router
from core.logs import configure_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Настраиваем логгер
    configure_logger()

    # 2) Подключаем Mongo и инициализируем Beanie
    client = AsyncIOMotorClient(settings.mongo.url)
    await init_beanie(
        database=client.get_database(settings.mongo.db_name),
        document_models=[ChatBot, Channel, Dialogue],
    )

    # разводим приложение
    yield

    # (опционально) здесь можно закрыть соединение с БД:
    # client.close()


def create_app() -> FastAPI:
    """
    Создаёт и настраивает FastAPI приложение с lifespan-хэндлером.
    """
    app = FastAPI(
        title="ChatBot API",
        lifespan=lifespan,     # <- здесь вместо on_event
    )
    app.include_router(api_router)
    return app


app = create_app()