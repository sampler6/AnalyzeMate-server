from fastapi import APIRouter

from api.schemas.base import BaseResponse

router = APIRouter()


@router.get("/check_startup/")
async def check_startup() -> BaseResponse:
    return BaseResponse(status_code=200, description="Application startup successfully completed")


print("ababa")
