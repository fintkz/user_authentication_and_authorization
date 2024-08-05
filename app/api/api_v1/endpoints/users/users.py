from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.responses import Response

from app import crud, models, schemas
from app.api import deps


router = APIRouter()


@router.post("/", response_model=schemas.Me)
def create_user(
    response: Response,
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    date: datetime = Depends(
        deps.timestamps.get_current_timezone_timestamp(timedelta(days=0))
    ),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = crud.user.create(db, obj_in=user_in)
    return schemas.Me(username=user.username, email=user.email, id = str(user.id))


@router.get("/me", response_model=schemas.Me)
def read_user_me(
    current_user: models.User = Depends(deps.user.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return schemas.Me(username=current_user.username, email=current_user.email, id = str(current_user.id))


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(deps.user.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=401, detail="The user doesn't have enough privileges"
        )
    return user


@router.delete("/me", response_model=schemas.Msg)
def delete_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.user.get_current_active_user),
) -> Any:
    crud.user.delete_user(db=db, user=current_user)
    return {"msg": "Success"}
