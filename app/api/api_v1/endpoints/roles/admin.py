from datetime import date, timedelta
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo import MongoClient
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import schemas, crud
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.get("/shadow-user/{shadow_username}", response_model=schemas.Msg)
def shadow_user(
    shadow_username: str,
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db),
    has_permission: bool = Depends(deps.has_permission("ShadowUser")),
) -> Any:
    if not has_permission:
        raise HTTPException(status_code=400, detail="You are not authorized.")

    shadow_user = crud.user.get_by_username(db, username=shadow_username)
    if not shadow_user:
        raise HTTPException(status_code=400, detail="Incorrect username")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(shadow_user.id, expires_delta=access_token_expires)

    response.set_cookie(
        key=settings.COOKIE_TOKEN_NAME,
        value=f"Bearer {access_token}",
        samesite="lax",
        expires=int(access_token_expires.total_seconds()),
    )

    return {"msg": "Authentication successful. Cookie set."}


@router.get("/all-users")
def get_all_users(
    db: Session = Depends(deps.get_db),
    created_after: date = Depends(deps.timestamps.get_current_timestamp(-timedelta(weeks=2))),
    created_before: date = Depends(deps.timestamps.get_current_timestamp(timedelta(days=1))),
    has_permission: bool = Depends(deps.has_permission("AdminSeeAllUsers")),
) -> Any:
    if not has_permission:
        raise HTTPException(status_code=403, detail="You are not authorized.")

    users = crud.user.get_all_users(db, created_after=created_after, created_before=created_before)
    return {"users": users}

