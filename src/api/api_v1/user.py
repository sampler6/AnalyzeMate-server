from auth.configuration import auth_backend
from auth.schemas.user import UserCreate, UserRead, UserUpdate
from auth.user_manager import fastapi_users
from fastapi import APIRouter

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])
