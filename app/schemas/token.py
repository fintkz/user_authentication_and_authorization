from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class SecureTokenPayload(BaseModel):
    sub: Optional[str] = None
    token_type: str
