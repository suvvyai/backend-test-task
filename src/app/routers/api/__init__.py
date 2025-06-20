from fastapi import APIRouter

from app.routers.api.hello_world import router as hello_world_router
from app.routers.api.channels import router as channels_router
from app.routers.api.webhook import router as webhook_router
from app.routers.api.bots import router as bots_router

api_router = APIRouter(prefix="/api")
api_router.include_router(hello_world_router)
api_router.include_router(channels_router)
api_router.include_router(webhook_router)
api_router.include_router(bots_router)
