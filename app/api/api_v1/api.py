from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    login,
    roles,
    users,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(roles.router, prefix="/roles")
api_router.include_router(users.router, prefix="/users")