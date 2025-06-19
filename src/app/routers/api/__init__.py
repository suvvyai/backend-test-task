from fastapi import APIRouter

from app.routers.api.channels import router as channels_router
from app.routers.api.hello_world import router as hello_world_router
from app.routers.api.messages import router as messages_router

router = APIRouter(prefix="/api")
router.include_router(hello_world_router)
router.include_router(messages_router, tags=["messages"])
router.include_router(channels_router, tags=["channels"])
