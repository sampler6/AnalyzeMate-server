from fastapi import APIRouter
from starlette.responses import JSONResponse

from api.api_v1.notification import router as notification_router
from api.api_v1.portfolio import router as portfolio_router
from api.api_v1.security import router as security_router
from api.api_v1.user import router as user_router

router = APIRouter()

router.include_router(user_router)
router.include_router(security_router, prefix="/securities", tags=["securities"])
router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
router.include_router(notification_router, prefix="/notification", tags=["notification"])


@router.get("/check_startup/")
async def check_startup() -> JSONResponse:
    return JSONResponse(status_code=204, content=None)
