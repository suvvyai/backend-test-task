from fastapi import APIRouter

from app.routers.api import api_router

router = APIRouter()
router.include_router(api_router)
