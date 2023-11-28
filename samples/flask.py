from flask import Flask, session, redirect, request
from logto import LogtoClient, LogtoConfig, LogtoException, Storage, UserInfoScope
from functools import wraps
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
        endpoint=os.getenv("LOGTO_ENDPOINT") or "replace-with-your-logto-endpoint",
        appId=os.getenv("LOGTO_APP_ID") or "replace-with-your-app-id",
        appSecret=os.getenv("LOGTO_APP_SECRET") or "replace-with-your-app-secret",
        scopes=[UserInfoScope.email, UserInfoScope.organizations, UserInfoScope.organization_roles], # Update scopes as needed
    ),
    SessionStorage(),
)

@app.route("/")
async def index():
    try:
        if client.isAuthenticated() is False:
            return "Not authenticated <a href='/sign-in'>Sign in</a>"
        return (
            "<br><a href='/protected'>View protected</a>"
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

### Below is an example of using decorator to protect a route ###

def authenticated(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if client.isAuthenticated() is False:
            return redirect("/sign-in") # Or directly call `client.signIn`
        return await func(*args, **kwargs)

    return wrapper

@app.route("/protected")
@authenticated
async def protected():
    try:
        return (
            "<h2>User info</h2>"
            + (await client.fetchUserInfo()).model_dump_json(
                indent=2,
                exclude_unset=True
            ).replace("\n", "<br>")
            + "<h2>ID token claims</h2>"
            + client.getIdTokenClaims().model_dump_json(
                indent=2,
                exclude_unset=True
            ).replace("\n", "<br>")
            + "<hr />"
            + "<a href='/'>Home</a>&nbsp;&nbsp;"
            + "<a href='/protected/organizations'>Organization token</a>&nbsp;&nbsp;"
            + "<a href='/sign-out'>Sign out</a>"
        )
    except LogtoException as e:
        return  "<h2>Error</h2>" + str(e) + "<br><hr /><a href='/sign-out'>Sign out</a>"

@app.route("/protected/organizations")
@authenticated
async def organizations():
    try:
        return (
            "<h2>Organization token</h2>"
            + (await client.getOrganizationTokenClaims("organization_id")) # Replace with a valid organization ID
            .model_dump_json(
                indent=2,
                exclude_unset=True
            ).replace("\n", "<br>")
            + "<hr />"
            + "<a href='/'>Home</a>&nbsp;&nbsp;"
            + "<a href='/sign-out'>Sign out</a>"
        )
    except LogtoException as e:
        return "<h2>Error</h2>" + str(e) + "<br><hr />a href='/sign-out'>Sign out</a>"
