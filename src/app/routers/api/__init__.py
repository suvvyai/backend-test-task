from fastapi import APIRouter

from src.app.routers.api.hello_world import router as hello_world_router
from src.app.routers.api.channels import router as channels_router

router = APIRouter(prefix="/api")
router.include_router(hello_world_router)
router.include_router(channels_router)
