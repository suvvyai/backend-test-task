from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse

# Импортируем новый роутер
from app.routers.api.channels import router as channels_router
from app.routers.api.hello_world import router as hello_world_router
from core.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await initialize_database()
    yield


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def index_to_docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="docs")

# Собираем основной роутер
main_router = APIRouter(prefix="/api")
main_router.include_router(hello_world_router)
main_router.include_router(channels_router)

app.include_router(main_router)