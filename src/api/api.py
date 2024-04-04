from fastapi import APIRouter

from api.api_v1.security import router as security_router
from api.api_v1.user import router as user_router
from api.schemas.base import TestResponse

router = APIRouter()

router.include_router(user_router)
router.include_router(security_router, prefix="/securities", tags=["securities"])


@router.get("/check_startup/")
async def check_startup() -> TestResponse:
    return TestResponse(description="Application startup successfully completed")
