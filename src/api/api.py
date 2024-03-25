from fastapi import APIRouter

from api.api_v1.user import router as user_router
from api.schemas.base import BaseResponse

router = APIRouter()

router.include_router(user_router)


@router.get("/check_startup/")
async def check_startup() -> BaseResponse:
    return BaseResponse(status_code=200, description="Application startup successfully completed")
