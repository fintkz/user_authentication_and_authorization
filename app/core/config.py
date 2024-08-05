import secrets
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
)
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "User Auth App"
    API_V1_STR: str = "/api/v1"
    SESSION_SECRET_KEY: str = secrets.token_urlsafe(32)

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
    ]
    JWT_TOKEN_KEY_LOGIN: str = secrets.token_urlsafe(32)
    JWT_TOKEN_KEY_SECURE: str = secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./data.db"
    SQLALCHEMY_TESTING_DATABASE_URI :str = "sqlite:///./test_data.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ACCESS_TOKEN_SECURE_EXPIRE_MINUTES: int = 60 * 24
    COOKIE_TOKEN_NAME: str = "api_access_token"
    COOKIE_TOKEN_SECURE_NAME: str = "secure_access_token"


settings = Settings()
