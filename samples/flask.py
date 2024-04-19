from flask import Flask, g, redirect, request, jsonify
from logto import LogtoException
from dotenv import load_dotenv
from samples.authenticated import authenticated
from samples.config import (
    APP_SECRET_KEY,
    LOGTO_POST_LOGOUT_REDIRECT_URI,
    LOGTO_REDIRECT_URI,
)
from samples.client import client

load_dotenv()
app = Flask(__name__)

app.secret_key = APP_SECRET_KEY


@app.route("/")
async def index():
    try:
        if client.isAuthenticated() is False:
            return (
                "<h1>Logto Flask sample</h1><p>Not authenticated</p>"
                + "<br/><a href='/sign-in'>Sign in</a>"
                + "<br><a href='/protected'>View protected (redirects to sign-in)</a>"
                + "<br><a href='/protected/no-redirect'>View protected (no redirect)</a>"
            )
        return (
            "<h1>Logto Flask sample</h1>"
            + "<a href='/protected'>View protected</a>"
            + "<br><a href='/protected/no-redirect'>View protected (no redirect)</a>"
            + "<br><a href='/protected/userinfo'>View userinfo</a>"
            + "<br><a href='/protected/organizations'>View organization token</a>"
            + "<br><a href='/sign-out'>Sign out</a>"
        )
    except LogtoException as e:
        return str(e) + "<br><a href='/sign-out'>Sign out</a>"


@app.route("/sign-in")
async def sign_in():
    return redirect(
        await client.signIn(
            redirectUri=LOGTO_REDIRECT_URI,
            interactionMode="signUp",  # Remove to show the sign-in as the first screen
        )
    )


@app.route("/sign-out")
async def sign_out():
    return redirect(
        await client.signOut(postLogoutRedirectUri=LOGTO_POST_LOGOUT_REDIRECT_URI)
    )


@app.route("/sign-in-callback")
async def callback():
    try:
        await client.handleSignInCallback(request.url)
        return redirect("/")
    except LogtoException as e:
        return str(e)


### Below are the examples of using decorator to protect routes ###

navigationHtml = (
    "<hr/><a href='/'>Home</a>&nbsp;&nbsp;" + "<a href='/sign-out'>Sign out</a>"
)


@app.route("/protected")
@authenticated(shouldRedirect=True)
async def protected():
    print(g.user)
    try:
        return (
            "<h2>User info</h2>"
            + g.user.model_dump_json(indent=2, exclude_unset=True).replace("\n", "<br>")
            + navigationHtml
        )
    except LogtoException as e:
        return "<h2>Error</h2>" + str(e) + "<br>" + navigationHtml


@app.route("/protected/userinfo")
@authenticated(shouldRedirect=True, fetchUserInfo=True)
async def protectedUserinfo():
    try:
        return (
            "<h2>User info</h2>"
            + g.user.model_dump_json(indent=2, exclude_unset=True).replace("\n", "<br>")
            + navigationHtml
        )
    except LogtoException as e:
        return "<h2>Error</h2>" + str(e) + "<br>" + navigationHtml


@app.route("/protected/no-redirect")
@authenticated()
async def protectedNoRedirect():
    return jsonify(
        {
            "message": "User is authenticated (try to access this route without being authenticated to see the difference)"
        }
    )


@app.route("/protected/organizations")
@authenticated(shouldRedirect=True)
async def organizations():
    try:
        return (
            "<h2>Organization token</h2>"
            + (
                await client.getOrganizationTokenClaims("organization_id")
            )  # Replace with a valid organization ID
            .model_dump_json(indent=2, exclude_unset=True)
            .replace("\n", "<br>")
            + navigationHtml
        )
    except LogtoException as e:
        return "<h2>Error</h2>" + str(e) + "<br>" + navigationHtml
