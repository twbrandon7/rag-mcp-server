from fastapi import APIRouter

from src.utils import router as utils_router
from src.auth.router import router as auth_router
from src.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(utils_router.router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
