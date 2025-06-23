from fastapi import APIRouter

from src.app.routers.api import router as api_router

router = APIRouter()
router.include_router(api_router)
