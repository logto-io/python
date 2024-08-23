import uuid
from typing import Optional

from fastapi import Depends, FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.responses import RedirectResponse

from logto import LogtoClient, LogtoConfig, Storage
from logto.models.oidc import UserInfoScope
from logto.Storage import PersistKey

r = Redis(host="localhost", port=6379, db=0)

LOGTO_SESSION = "logto:session"
LOGTO_SESSION_ID = "session"

# frontend site url
SITE_URL = ""

# Logto settings
LOGTO_ENDPOINT = ""
LOGTO_APP_ID = ""
LOGTO_APP_SECRET = ""


class RedisStorage(Storage):
    def __init__(self, session_id: str):
        self._key = f"{LOGTO_SESSION}:{session_id}"

    async def get(self, key: PersistKey) -> Optional[str]:
        return await r.hget(self._key, key)

    async def set(self, key: PersistKey, value: Optional[str]) -> None:
        await r.hset(self._key, key, value)

    async def delete(self, key: PersistKey) -> None:
        await r.hdel(self._key, key)


def get_session_id(request: Request) -> str:
    return request.cookies.get(LOGTO_SESSION_ID) or ""


def get_logto_client(session_id: str = Depends(get_session_id)) -> LogtoClient:
    return get_client(session_id)


def get_client(session_id: str) -> LogtoClient:
    client = LogtoClient(
        LogtoConfig(
            endpoint=LOGTO_ENDPOINT,
            appId=LOGTO_APP_ID,
            appSecret=LOGTO_APP_SECRET,
            scopes=[UserInfoScope.email],
        ),
        storage=RedisStorage(session_id),
    )
    return client


async def get_current_user(
    client: LogtoClient = Depends(get_logto_client),
):
    return await client.fetchUserInfo()


app = FastAPI()


@app.get("/callback")
async def callback(
    request: Request,
    client: LogtoClient = Depends(get_logto_client),
) -> RedirectResponse:
    await client.handleSignInCallback(f"{SITE_URL}/api/callback?{request.url.query}")
    userinfo = await client.fetchUserInfo()
    # do something with userinfo, like save it to database
    return RedirectResponse(url=SITE_URL)


# frontend should point here when user click login
@app.get("/sign-in")
async def sign_in() -> RedirectResponse:
    session_id = uuid.uuid4().hex
    client = get_client(session_id)
    response = RedirectResponse(
        await client.signIn(
            redirectUri=f"{SITE_URL}/api/callback",
        )
    )
    response.set_cookie(LOGTO_SESSION_ID, session_id, httponly=True)
    return response


# frontend should point here when user click logout
@app.get("/sign-out", dependencies=[Depends(get_current_user)])
async def sign_out(
    client: LogtoClient = Depends(get_logto_client),
) -> RedirectResponse:
    response = RedirectResponse(await client.signOut(postLogoutRedirectUri=SITE_URL))
    response.delete_cookie(LOGTO_SESSION_ID)
    return response


@app.get("/user")
async def get_user(user=Depends(get_current_user)):
    return user
