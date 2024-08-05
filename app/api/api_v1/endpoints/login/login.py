from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailError, validate_email
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import Response

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Msg)
def login_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif user.email is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "You don't have an email associated with your "
                "account yet. Please add an email and try again."
            ),
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_secure_expires = timedelta(minutes=settings.ACCESS_TOKEN_SECURE_EXPIRE_MINUTES)
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    # This is the regular access token
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
        token_type="login",
    )

    # 'secure' is the second access cookie we create for endpoints needing
    # extra security e.g. transactions involving money,
    # opening websocket connections, etc.
    #
    # We also use a shorter expiration time for it, so the client will need to
    # transparently refresh the token if necessary
    access_token_secure = security.create_access_token(
        user.id,
        expires_delta=access_token_secure_expires,
        token_type="secure",
    )

    response.set_cookie(
        key=settings.COOKIE_TOKEN_NAME,
        value=f"Bearer {access_token}",
        samesite="lax",
        httponly=True,
        expires=int(access_token_expires.total_seconds()),
    )

    response.set_cookie(
        key=settings.COOKIE_TOKEN_SECURE_NAME,
        value=access_token_secure,
        samesite="strict",
        httponly=True,
        secure=False,
        expires=int(access_token_secure_expires.total_seconds()),
    )

    return {"msg": "Authentication successful. Cookie set."}


@router.get(
    "/logout", dependencies=[Depends(deps.user.get_current_user)], response_model=schemas.Msg
)
def logout(
    request: Request,
    response: Response,
) -> Any:
    response.delete_cookie(
        key=settings.COOKIE_TOKEN_NAME,
    )
    response.delete_cookie(
        key=settings.COOKIE_TOKEN_SECURE_NAME,
    )
    return {"msg": "Logout successful. Cookie deleted."}


@router.post("/login-and-update", response_model=schemas.Msg)
def external_user_login(
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    new_password: str = Body(...),
    new_email: EmailStr = Body(None),
) -> Any:
    """
    Verify user and update password and/or email
    and
    Get OAuth2 compatible token for login and future requests
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    current_user_data = jsonable_encoder(user)
    user_in = schemas.UserUpdate(**current_user_data)

    if new_email:
        existing_user = crud.user.get_by_email(db, email=new_email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use, please try again.")
        try:
            validate_email(new_email)
        except EmailError:
            raise HTTPException(status_code=400, detail="Invalid email, please try again.")
    else:
        raise HTTPException(status_code=400, detail="Invalid email, please try again.")

    if new_password is None or new_password == "":
        raise HTTPException(status_code=400, detail="New password is invalid, please try again.")

    user_in.email = new_email
    user_in.password = new_password
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_secure_expires = timedelta(minutes=settings.ACCESS_TOKEN_SECURE_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
        token_type="login",
    )
    access_token_secure = security.create_access_token(
        user.id,
        expires_delta=access_token_secure_expires,
        token_type="secure",
    )

    response.set_cookie(
        key=settings.COOKIE_TOKEN_NAME,
        value=f"Bearer {access_token}",
        samesite="lax",
        httponly=True,
        expires=int(access_token_expires.total_seconds()),
    )

    response.set_cookie(
        key=settings.COOKIE_TOKEN_SECURE_NAME,
        value=access_token_secure,
        samesite="strict",
        httponly=True,
        secure=True,
        expires=int(access_token_secure_expires.total_seconds()),
    )

    return {"msg": "Authentication successful. Cookie set."}
