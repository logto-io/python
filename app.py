from flask import Flask, session, redirect, request
from logto import LogtoClient, LogtoConfig, Storage

app = Flask(__name__)

app.secret_key = b'1234567890abcdef'

class SessionStorage(Storage):
  def get(self, key: str) -> str | None:
    return session.get(key, None)
  
  def set(self, key: str, value: str | None) -> None:
    session.permanent = True
    session[key] = value
    session.modified = True
  
  def delete(self, key: str) -> None:
    session.permanent = True
    session.pop(key, None)
    session.modified = True

client = LogtoClient(
  LogtoConfig(
    endpoint="http://logto-endpoint.app",
    appId="replace-with-your-app-id",
    appSecret="replace-with-your-app-secret",
    resources=["https://logto-endpoint.app/api"], # Remove if you don't need to access the default Logto API
    scopes=["email"],
  ),
  SessionStorage(),
)

@app.route("/")
async def index():
  try:
    if client.isAuthenticated() is False:
      return "Not authenticated <a href='/sign-in'>Sign in</a>"
    return (await client.fetchUserInfo()).model_dump_json(exclude_unset=True) + \
      "<br>" + client.getIdTokenClaims().model_dump_json(exclude_unset=True) + \
      "<br>" + (await client.getAccessTokenClaims("https://logto-endpoint.app/api")).model_dump_json(exclude_unset=True) + \
      "<br><a href='/sign-out'>Sign out</a>"
  except LogtoClient.LogtoException as e:
    return str(e)

@app.route("/sign-in")
async def sign_in():
  return redirect(await client.signIn('http://127.0.0.1:5000/callback', 'signUp'))

@app.route("/sign-out")
async def sign_out():
  return redirect(await client.signOut('http://127.0.0.1:5000/'))

@app.route("/callback")
async def callback():
  try:
    await client.handleSignInCallback(request.url)
    return redirect('/')
  except LogtoClient.LogtoException as e:
    return str(e)
