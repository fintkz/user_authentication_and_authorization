from fastapi import APIRouter

from app.api.api_v1.endpoints.roles import admin

router = APIRouter()
router.include_router(admin.router, prefix="/admin", tags=["roles/admin"])
