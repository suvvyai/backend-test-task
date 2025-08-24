from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse


from app.routers.api.channels import router as channels_router
from app.routers.api.hello_world import router as hello_world_router
from app.routers.api.webhook import router as webhook_router
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


main_router = APIRouter(prefix="/api")
main_router.include_router(hello_world_router)
main_router.include_router(channels_router)
main_router.include_router(webhook_router)

app.include_router(main_router)
