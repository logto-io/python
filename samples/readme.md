# 1. Install dependencies

First, make sure to have Python `3.11.4`+ installed.

Then, create an `venv`:

`python3 -m venv .`

Install requirements (`requirements.txt` should install all dependencies, but `requirements_full.txt` contains a full list of dependencies (shouldn't be necessary))

`pip install -r requirements.txt`

# 2. Setup config.py

Go to your Logto Admin and create your application, you will get and set some information:

`Logto endpoint` - Is given by logto (usually `http://localhost:3001/` when self-host)
`App ID` - Is also given by logto
`App Secret` - Is also given by logto
`Redirect URIs` - You need to set an URI that the Logto will redirect after the sign-up (successful or not), for example `http://localhost:5000/callback` (your application)
`Post Sign-out Redirect URIs` - When the user sign-out the Logto will redirect to this page, it can be the 'home' page like `http://localhost:5000`

Now on `config.py` you need to set the values:

```py
app_id = 'App ID'
app_secret = 'The App Secret'
redirect_uri_callback = 'Redirect URIs' #configure in logto admin
post_logout_redirect_uri = 'Post Sign-out Redirect URIs' #configure in logto admin
core_endpoint = 'Logto endpoint' #do not add a final forward slash '/', for example, if the Logto endpoint is http://localhost:3001/, it should be set like http://localhost:3001 (THIS IS VERY IMPORTANT)
issuer = 'http://localhost:3001/oidc' #it's the core_endpoint + '/oidc'
jwks_uri = 'http://localhost:3001/oidc/jwks' #it's the core_endpoint + '/oidc/jwks'

# Global variables for JWKS caching
JWKS_CACHE = None
JWKS_LAST_FETCHED = 0
JWKS_REFRESH_INTERVAL = 86400  # Refresh every 24 hours (86400 seconds)
```

**NOTE**: You may also configure a secret key to your flask app in `main.py` at: `app.secret_key = 'supersecret'`

# 3. Run and test it

`python3 main.py`

Go into `http://localhost:5000`, you should see a `Sign-Up` button, upon clicking it, you should be redirected to Logto sign-up/sign-in page. Once registered, you should go back to `http://localhost:5000` and see your user data dump.

You may utilize other browser and incognito mode to enter `http://localhost:5000` and test multiple users.

Then, you can Sign-out by clicking on `Sign-out` button.
 
# 3. Protect your routes

You have many ways to accomplish this. For example:

You can call client.isAuthenticated() and client.fetchUserInfo() to both check if the user is authenticated and can proceed with the request and to get the user info.

```py
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
```

An decorator is also available, it will validate the JWT token. Optionally you may send an `redirect_url` parameter to this decorator, if it identify that the user is not authenticated or token is invalid, it will be redirected to the given url (sign-up page for example)

You can get user data using: `user_info = getattr(_request_ctx_stack.top, 'user_info', None)`.

```py
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
```

The user data object looks like:

```json
{
   "sub":"zpt64vlx91v6",
   "name":null,
   "username":"test",
   "picture":null
}
```

Where `sub` is the user identifier (you may verify it on the Logto admin user management page).


# Conclusion

With this, you can proceed to create a service where users can create accounts. You can authenticate users and proceed with your business-logic with their given id to refeer to.

You also would change how you load your config.py to a more secure approach.