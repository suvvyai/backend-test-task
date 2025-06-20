from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers.api import api_router
from core.logs.handlers import setup_logging
from core.database.registry import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Настраиваем логирование
    setup_logging()
    # 2) Инициализируем БД
    await initialize_database()
    # Всё готово — разворачиваем приложение
    yield
    # (опционально) здесь можно закрыть соединения или сделать очистку ресурсов


def create_app() -> FastAPI:

    app = FastAPI(
        title="ChatBot API",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()
