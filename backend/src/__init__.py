from fastapi import APIRouter

from src.utils import router as utils_router
from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.projects.router import router as projects_router
from src.urls.router import router as urls_router
from src.chunks.router import router as chunks_router

api_router = APIRouter()
api_router.include_router(utils_router.router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(urls_router, prefix="/projects", tags=["urls"])
api_router.include_router(chunks_router, prefix="/projects", tags=["chunks"])
