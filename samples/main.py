from flask import Flask, request, redirect, session, jsonify, _request_ctx_stack
from flask_restful import Resource, Api
from logto import LogtoClient, LogtoConfig, Storage
from functools import wraps
from jose import jwt
from six.moves.urllib.request import urlopen
import json
import time
from config import app_id, app_secret, redirect_uri_callback, post_logout_redirect_uri, core_endpoint, issuer, jwks_uri, JWKS_CACHE, JWKS_LAST_FETCHED, JWKS_REFRESH_INTERVAL

# Custom session storage class for Logto integration with Flask
class SessionStorage(Storage):
    def get(self, key: str) -> str | None:
        # Retrieve a value from Flask session storage
        return session.get(key)

    def set(self, key: str, value: str | None) -> None:
        # Set a value in Flask session storage
        session[key] = value

    def delete(self, key: str) -> None:
        # Delete a value from Flask session storage
        session.pop(key, None)

# Logto client configuration
client = LogtoClient(
    LogtoConfig(
        endpoint=core_endpoint,
        appId=app_id,
        appSecret=app_secret
    ),
    storage=SessionStorage()
)

# Function to get or refresh JWKS - It will run every 24 hours and cache it (so it doesn't make a request to the logto server at each token validation)
def get_jwks():
    global JWKS_CACHE, JWKS_LAST_FETCHED
    current_time = time.time()

    # Refresh JWKS if cache is old or not set
    if JWKS_CACHE is None or (current_time - JWKS_LAST_FETCHED > JWKS_REFRESH_INTERVAL):
        jwks_data = urlopen(jwks_uri)  # jwks_uri is set in config.py
        JWKS_CACHE = json.loads(jwks_data.read())
        JWKS_LAST_FETCHED = current_time

    return JWKS_CACHE

# JWT validation function
def validate_jwt(token):
    # Retrieve JSON Web Key Set (JWKS) from Logto server
    jwks = get_jwks()

    # Decode the JWT header
    header = jwt.get_unverified_header(token)
    # Find the matching RSA key
    rsa_key = next((key for key in jwks['keys'] if key['kid'] == header['kid']), None)
    if rsa_key is None:
        raise Exception("RSA key not found")

    # Decode the JWT payload and verify its integrity and authenticity
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=[header['alg']],
        audience=app_id, #app_id is set on config.py
        issuer=issuer, #issuer is set on config.py
        options={'verify_at_hash': False} # it's not verifying hash, this can be improved
    )

    # Check if the token is expired
    if time.time() > payload['exp']:
        raise Exception('Token is expired.')

    return payload

# Decorator to require authentication and provide user info, you can provide an redirect_url, so if the user is not authenticatd, it will be redirected to the given url (like go to sign-up page for example)
def requires_auth_with_user_info(redirect_url=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = client.getIdToken()

            if not token:
                if redirect_url:
                    return redirect(redirect_url)
                return jsonify({"error": "No token found"}), 401

            try:
                payload = validate_jwt(token)
                _request_ctx_stack.top.user_info = payload
            except Exception as e:
                if redirect_url:
                    return redirect(redirect_url)
                return jsonify({'error': 'Invalid token', 'code': 401}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Flask application setup
app = Flask(__name__)
app.secret_key = 'supersecret' #CHANGE THIS!
api = Api(app)
port = 5000

# Sign-in route
@app.route("/sign-in")
async def sign_in():
    # Redirect to Logto sign-in URL
    return redirect(await client.signIn(
        redirectUri=redirect_uri_callback,
        interactionMode="signUp"
    ))

# Callback route for handling the sign-in response
@app.route("/callback")
async def callback():
    try:
        await client.handleSignInCallback(request.url)
        return redirect("http://localhost:5000")
    except Exception as e:
        return "Error: " + str(e)

# Sign-out route
@app.route("/sign-out")
async def sign_out():
    return redirect(await client.signOut(postLogoutRedirectUri=post_logout_redirect_uri))

# Home route
@app.route("/")
async def home():
    if not client.isAuthenticated(): #You can check if the client is authenticated using this funtion
        return "Not authenticated <a href='/sign-in'>Sign in</a>"

    id_token_claims = client.getIdTokenClaims()
    user_info = await client.fetchUserInfo() # You may fetch user info using this

    return (
        id_token_claims.model_dump_json(exclude_unset=True) + "<br>" +
        user_info.model_dump_json(exclude_unset=True) + "<br><a href='/sign-out'>Sign out</a>"
    )

# Protected route example
@app.route('/protected')
@requires_auth_with_user_info()
def protected_route():
    user_info = getattr(_request_ctx_stack.top, 'user_info', None) #You may also fetch user info using this
    if user_info:
        return jsonify({"message": f"Hello, {user_info['username']}"})
    else:
        return jsonify({"error": "User info not available"}), 401

# Another protected route with redirect (will redirect the non authenticated user to /sign-in)
@app.route('/protected_redirect')
@requires_auth_with_user_info(redirect_url='/sign-in')
def protected_redirect():
    user_info = getattr(_request_ctx_stack.top, 'user_info', None)
    if user_info:
        return jsonify({"message": f"Hello, {user_info['username']}"})
    else:
        return jsonify({"error": "User info not available"}), 401

# Main function to run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
