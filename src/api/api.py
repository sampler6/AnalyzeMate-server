from fastapi import APIRouter

from api.api_v1.security import router as security_router
from api.api_v1.user import router as user_router

router = APIRouter()

router.include_router(user_router)
router.include_router(security_router, prefix="/securities", tags=["securities"])
