import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "login",
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}

    # We use a different secret for each type of token
    if token_type == "secure":
        secret_key = settings.JWT_TOKEN_KEY_SECURE
        to_encode["token_type"] = token_type
    elif token_type == "login":
        # The format of this JWT is set by the OAuth 2.0 specification
        # so we don't add additional fields here
        secret_key = settings.JWT_TOKEN_KEY_LOGIN
    else:
        secret_key = settings.JWT_TOKEN_KEY_LOGIN
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_temporary_password(length: int) -> Tuple[str, str]:
    # Generate a temporary password for users who sign up with an external account
    # and return both the password and the hashed password
    temporary_password_string = string.ascii_letters + string.hexdigits
    temporary_password = "".join(
        secrets.choice(temporary_password_string) for i in range(length)
    )
    return temporary_password, pwd_context.hash(temporary_password)
