from flask import Flask, session, redirect, request
from logto import LogtoClient, LogtoConfig, LogtoException, Storage
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

app.secret_key = b"1234567890abcdef"  # Replace with your own secret key


class SessionStorage(Storage):
    def get(self, key: str) -> str | None:
        return session.get(key, None)

    def set(self, key: str, value: str | None) -> None:
        session[key] = value

    def delete(self, key: str) -> None:
        session.pop(key, None)


client = LogtoClient(
    LogtoConfig(
        endpoint="http://localhost:3001",  # Replace with your Logto endpoint
        appId=os.getenv("LOGTO_APP_ID") or "replace-with-your-app-id",
        appSecret=os.getenv("LOGTO_APP_SECRET") or "replace-with-your-app-secret",
        resources=[
            "https://default.logto.app/api",
            "https://shopping.api",
        ],  # Remove if you don't need to access the default Logto API
        scopes=["email"],
    ),
    SessionStorage(),
)


@app.route("/")
async def index():
    try:
        if client.isAuthenticated() is False:
            return "Not authenticated <a href='/sign-in'>Sign in</a>"
        return (
            (await client.fetchUserInfo()).model_dump_json(exclude_unset=True)
            + "<br>"
            + client.getIdTokenClaims().model_dump_json(exclude_unset=True)
            + "<br>"
            + (
                await client.getAccessTokenClaims("https://default.logto.app/api")
            ).model_dump_json(exclude_unset=True)
            + "<br><a href='/sign-out'>Sign out</a>"
        )
    except LogtoException as e:
        return str(e) + "<br><a href='/sign-out'>Sign out</a>"


@app.route("/sign-in")
async def sign_in():
    return redirect(
        await client.signIn(
            redirectUri="http://127.0.0.1:5000/callback", interactionMode="signUp"
        )
    )


@app.route("/sign-out")
async def sign_out():
    return redirect(
        await client.signOut(postLogoutRedirectUri="http://127.0.0.1:5000/")
    )


@app.route("/callback")
async def callback():
    try:
        await client.handleSignInCallback(request.url)
        return redirect("/")
    except LogtoException as e:
        return str(e)
