from auth.configuration import auth_backend
from auth.models.user import User
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
    prefix="/auth/jwt",
    tags=["auth"],
)
