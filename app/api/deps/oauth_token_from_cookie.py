from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    This class implements OAuth2 but with the password in the cookie
    rather than from a header
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(
            flows=flows, scheme_name=scheme_name, auto_error=auto_error
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get(settings.COOKIE_TOKEN_NAME)
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


class CustomOAuth2PasswordBearerWithCookie(OAuth2PasswordBearerWithCookie):
    """
    This custom class allows us to process either regular HTTP requests
    or websocket connections. They both have cookies, but come as either Request
    Objects or WebSocket objects

    We duck type them into the parent class based on whichever one is defined
    """

    async def __call__(
        self, request: Request = None, websocket: WebSocket = None
    ):
        try:
            return await super().__call__(request or websocket)
        except HTTPException as e:
            if websocket is not None:
                # This is a websocket that has called for authentication
                # websockets don't return HTTPExceptions; they just close the connection
                # We need to upgrade fastapi to raise a proper WebSocketException
                # for now, we raise WebSocketDisconnect instead
                # This is one option, to just close the websocket directly
                # but then the rest of the code still executes and will eventually cause a
                # server error anyway
                # await websocket.close()
                # This still raises a server error but the server should recover fine
                # And it will halt any further processing
                raise WebSocketDisconnect(code=4001) from e
            else:
                raise e


# This uses the JWT token stored in our cookie
reusable_oauth2 = CustomOAuth2PasswordBearerWithCookie(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
