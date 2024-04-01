from auth.configuration import auth_backend
from auth.models.user import User
from auth.schemas.user import UserCreate, UserRead, UserUpdate
from auth.user_manager import get_user_manager
from fastapi import APIRouter
from fastapi_users import FastAPIUsers

router = APIRouter()

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

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
