# Logto Python SDK tutorial

This tutorial will show you how to integrate Logto into your Python web application.

- The example uses Flask, but the concepts are the same for other frameworks.
- This tutorial assumes your website is hosted on `https://your-app.com/`.
- Logto SDK leverages coroutines, remember to use `await` when calling async functions.

## Table of contents

- [Logto Python SDK tutorial](#logto-python-sdk-tutorial)
  - [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Integration](#integration)
    - [Init LogtoClient](#init-logtoclient)
    - [Implement the sign-in route](#implement-the-sign-in-route)
    - [Implement the callback route](#implement-the-callback-route)
    - [Implement the home page](#implement-the-home-page)
    - [Implement the sign-out route](#implement-the-sign-out-route)
    - [Checkpoint: Test your application](#checkpoint-test-your-application)
  - [Protect your routes](#protect-your-routes)
  - [Scopes and claims](#scopes-and-claims)
    - [Special ID token claims](#special-id-token-claims)
  - [API resources](#api-resources)
    - [Configure Logto client](#configure-logto-client)
    - [Fetch access token for the API resource](#fetch-access-token-for-the-api-resource)
    - [Fetch organization token for user](#fetch-organization-token-for-user)

## Installation
```bash
pip install logto # or `poetry add logto` or whatever you use
```

## Integration

### Init LogtoClient

```python
from logto import LogtoClient, LogtoConfig

client = LogtoClient(
    LogtoConfig(
        endpoint="https://you-logto-endpoint.app",  # Replace with your Logto endpoint
        appId="replace-with-your-app-id",
        appSecret="replace-with-your-app-secret",
    ),
)
```

Also replace the default memory storage with a persistent storage, for example:

```python
from logto import LogtoClient, LogtoConfig, Storage
from flask import session
from typing import Union

class SessionStorage(Storage):
    def get(self, key: str) -> Union[str, None]:
        return session.get(key, None)

    def set(self, key: str, value: Union[str, None]) -> None:
        session[key] = value

    def delete(self, key: str) -> None:
        session.pop(key, None)

client = LogtoClient(
    LogtoConfig(...),
    storage=SessionStorage(),
)
```

See [Storage](./api.md#logto.Storage.Storage) for more details.


### Implement the sign-in route

In your web application, add a route to properly handle the sign-in request from users. Let's use `/sign-in` as an example:

```python
@app.route("/sign-in")
async def sign_in():
    # Get the sign-in URL and redirect the user to it
    return redirect(await client.signIn(
        redirectUri="https://your-app.com/callback",
    ))
```

Replace `https://your-app.com/callback` with the callback URL you set in your Logto Console for this application.

If you want to show the sign-up page on the first screen, you can set `interactionMode` to `signUp`:

```python
@app.route("/sign-in")
async def sign_in():
    return redirect(await client.signIn(
        redirectUri="https://your-app.com/callback",
        interactionMode="signUp", # Show the sign-up page on the first screen
    ))
```

Now, whenever your users visit `https://your-app.com/sign-in`, it will start a new sign-in attempt and redirect the user to the Logto sign-in page.

> **Note**
> Creating a sign-in route isn't the only way to start a sign-in attempt. You can always use the `signIn` method to get the sign-in URL and redirect the user to it.

### Implement the callback route

After the user signs in, Logto will redirect the user to the callback URL you set in the Logto Console. In this example, we use `/callback` as the callback URL:

```python
@app.route("/callback")
async def callback():
    try:
        await client.handleSignInCallback(request.url) # Handle a lot of stuff
        return redirect("/") # Redirect the user to the home page after a successful sign-in
    except Exception as e:
        # Change this to your error handling logic
        return "Error: " + str(e)
```

### Implement the home page

Here we implement a simple home page for demonstration:

- If the user is not signed in, show a sign-in button;
- If the user is signed in, show some basic information about the user.

```python
@app.route("/")
async def home():
    if client.isAuthenticated() is False:
        return "Not authenticated <a href='/sign-in'>Sign in</a>"

    return (
        # Get local ID token claims
        client.getIdTokenClaims().model_dump_json(exclude_unset=True)
        + "<br>"
        # Fetch user info from Logto userinfo endpoint
        (await client.fetchUserInfo()).model_dump_json(exclude_unset=True)
        + "<br><a href='/sign-out'>Sign out</a>"
    )
```

Our data models are based on [pydantic](https://docs.pydantic.dev/), so you can use `model_dump_json` to dump the data model to JSON.

Adding `exclude_unset=True` will exclude unset fields from the JSON output, which makes the output more precise.

For example, if we didn't request the `email` scope when signing in, and the `email` field will be excluded from the JSON output. However, if we requested the `email` scope, but the user doesn't have an email address, the `email` field will be included in the JSON output with a `null` value.

To learn more about scopes and claims, see [Scopes and claims](#scopes-and-claims).

### Implement the sign-out route

To clean up the Python session and Logto session, a sign-out route can be implemented as follows:

```python
@app.route("/sign-out")
async def sign_out():
    return redirect(
        # Redirect the user to the home page after a successful sign-out
        await client.signOut(postLogoutRedirectUri="https://your-app.com/")
    )
```

`postLogoutRedirectUri` is optional, and if not provided, the user will be redirected to a Logto default page after a successful sign-out (without redirecting back to your application).

> The name `postLogoutRedirectUri` is from the [OpenID Connect RP-Initiated Logout](https://openid.net/specs/openid-connect-rpinitiated-1_0.html) specification. Although Logto uses "sign-out" instead of "logout", the concept is the same.

### Checkpoint: Test your application

Now, you can test your application:

1. Visit `https://your-app.com/`, and you should see a "Not authenticated" message with a "Sign in" button.
2. Click the "Sign in" button, and you should be redirected to the Logto sign-in page.
3. After you sign in, you should be redirected back to `https://your-app.com/`, and you should see your user info and a "Sign out" button.
4. Click the "Sign out" button, and you should be redirected back to `https://your-app.com/`, and you should see a "Not authenticated" message with a "Sign in" button.

## Protect your routes

Now, you have a working sign-in flow, but your routes are still unprotected. Per the framework you use, you can create a decorator such as `@authenticated` to protect your routes. For example:

```python
def authenticated(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if client.isAuthenticated() is False:
            return redirect("/sign-in") # Or directly call `client.signIn`
        return await func(*args, **kwargs)

    return wrapper
```

Then, you can use the decorator to protect your routes:

```python
@app.route("/protected")
@authenticated
async def protected():
    return "Protected page"
```

You can also create a middleware to achieve the same goal.

## Scopes and claims

Both of "scope" and "claim" are terms from the OAuth 2.0 and OpenID Connect (OIDC) specifications. In OIDC, there are some optional [scopes and claims conventions](https://openid.net/specs/openid-connect-core-1_0.html#Claims) to follow. Logto uses these conventions to define the scopes and claims for the ID token.

In short, when you request a scope, you will get the corresponding claims in the ID token. For example, if you request the `email` scope, you will get the `email` and `email_verified` claims in the ID token.

By default, Logto SDK requests three scopes: `openid`, `profile`, and `offline_access`. You can add more scopes when configuring the Logto client:

```python
client = LogtoClient(
    LogtoConfig(
        # ...other configs
        scopes=["email", "phone"], # Add more scopes
    ),
)

# or

client = LogtoClient(
    LogtoConfig(
        # ...other configs
        scopes=[UserInfoScope.email, UserInfoScope.profile], # Same result
    ),
)
```

> **Note**
> For now, there's no way to remove the default scopes without mutating the `scopes` list.

See [UserInfoScope](./api.md#logto.models.oidc.UserInfoScope) for a list of supported scopes and its mapped claims.

### Special ID token claims

Considering performance and the data size, Logto doesn't include all the claims in the ID token, such as `custom_data` which could be a large JSON object. To fetch these claims, you can use the `fetchUserInfo` method:

```python
(await client.fetchUserInfo()).custom_data # Get the custom_data claim
```

See [UserInfoScope](./api.md#logto.models.oidc.UserInfoScope) for details.

## API resources

We recommend to read [🔐 Role-Based Access Control (RBAC)](https://docs.logto.io/docs/recipes/rbac/) first to understand the basic concepts of Logto RBAC and how to set up API resources properly.

### Configure Logto client

Once you have set up the API resources, you can add them when configuring the Logto client:

```python
client = LogtoClient(
    LogtoConfig(
        # ...other configs
        resources=["https://shopping.your-app.com/api", "https://store.your-app.com/api"], # Add API resources
    ),
)
```

Each API resource has its own permissions (scopes). For example, the `https://shopping.your-app.com/api` resource has the `shopping:read` and `shopping:write` permissions, and the `https://store.your-app.com/api` resource has the `store:read` and `store:write` permissions.

To request these permissions, you can add them when configuring the Logto client:

```python
client = LogtoClient(
    LogtoConfig(
        # ...other configs
        scopes=["shopping:read", "shopping:write", "store:read", "store:write"],
        resources=["https://shopping.your-app.com/api", "https://store.your-app.com/api"],
    ),
)
```

You may notice that scopes are defined separately from API resources. This is because [Resource Indicators for OAuth 2.0](https://www.rfc-editor.org/rfc/rfc8707.html) specifies the final scopes for the request will be the cartesian product of all the scopes at all the target services.

Thus, in the above case, scopes can be simplified from the definition in Logto, both of the API resources can have `read` and `write` scopes without the prefix. Then, in the Logto config:

```python
client = LogtoClient(
    LogtoConfig(
        # ...other configs
        scopes=["read", "write"],
        resources=["https://shopping.your-app.com/api", "https://store.your-app.com/api"],
    ),
)
```

For every API resource, it will request for both `read` and `write` scopes.

> **Note**
> It is fine to request scopes that are not defined in the API resources. For example, you can request the `email` scope even if the API resources don't have the `email` scope available. Unavailable scopes will be safely ignored.

After the successful sign-in, Logto will issue proper scopes to every API resource according to the user's roles.

### Fetch access token for the API resource

To fetch the access token for a specific API resource, you can use the `getAccessToken` method:

```python
accessToken = await client.getAccessToken("https://shopping.your-app.com/api")
# or
claims = await client.getAccessTokenClaims("https://shopping.your-app.com/api")
```

This method will return a JWT access token that can be used to access the API resource, if the user has the proper permissions. If the current cached access token has expired, this method will automatically try to use the refresh token to get a new access token.

If failed by any reason, this method will return `None`.

### Fetch organization token for user

If organization is new to you, please read [🏢 Organizations (Multi-tenancy)](https://docs.logto.io/docs/recipes/organizations/) to get started.

You need to add `UserInfoScope.organizations` scope when configuring the Logto client:

```python
from logto import LogtoClient, LogtoConfig, UserInfoScope

client = LogtoClient(
    LogtoConfig(
        # ...other configs
        scopes=[UserInfoScope.organizations],
    ),
)
```

Once the user is signed in, you can fetch the organization token for the user:

```python
# Replace the parameter with a valid organization ID.
# Valid organization IDs for the user can be found in the ID token claim `organizations`.
organizationToken = await client.getOrganizationToken("organization-id")
# or
claims = await client.getOrganizationTokenClaims("organization-id")
```
