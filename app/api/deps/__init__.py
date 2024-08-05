import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, WebSocket, status
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.core.config import settings

from . import timestamps, user
from .db import get_db
from .oauth_token_from_cookie import reusable_oauth2


def is_request_secure(
    request: Request = None,
    websocket: WebSocket = None,
    user: models.User = Depends(user.get_current_user),
):
    """
    This checks the secure_access_token which is a stricter cookie to completely
    disable cross-site requests. If the cookie is present and valid, then this is not
    a cross-site request and the request can be considered secure from CSRF and XSS attacks.

    Use this check for extra security on important endpoints
    e.g. involving money or transactions, or starting a WebSocket, etc.

    :param websocket:
    :param request:
    :param user:
    :return:
    """

    if request is not None:
        cookies = request.cookies
    elif websocket is not None:
        cookies = websocket.cookies
    else:
        cookies = None

    if settings.COOKIE_TOKEN_SECURE_NAME not in cookies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    try:
        payload = jwt.decode(
            cookies[settings.COOKIE_TOKEN_SECURE_NAME],
            settings.JWT_TOKEN_KEY_SECURE,
            algorithms=[security.ALGORITHM],
        )
    except (jwt.JWTError, jwt.ExpiredSignatureError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    token_data = schemas.SecureTokenPayload(**payload)

    if (token_data.token_type != "secure") or (token_data.sub != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return True


def has_permission(permission: str, target_user_id: uuid.UUID | None = None):
    def factory(
        db: Session = Depends(get_db),
        user: models.User = Depends(user.get_current_active_user),
    ) -> bool:
        permission_record = (
            db.query(models.Permission).filter_by(permission_name=permission).first()
        )
        if permission_record is None:
            return False
        roles = db.query(models.User).filter_by(id=user.id).join(models.User.roles)
        if target_user_id:
            roles = roles.filter_by(target_user_id=target_user_id)

        return bool(
            roles.join(models.join_tables.UsersRole.role)
            .join(models.Role.permissions)
            .filter_by(id=permission_record.id)
            .first()
        )

    return factory

