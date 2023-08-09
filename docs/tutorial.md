# Logto Python SDK tutorial

This tutorial will show you how to integrate Logto into your Python web application.

- The example uses Flask, but the concepts are the same for other frameworks.
- This tutorial assumes your website is hosted on `https://your-app.com/`.
- Logto SDK leverages coroutines, remember to use `await` when calling async functions.

## Table of contents

- [Logto Python SDK tutorial](#logto-python-sdk-tutorial)
  - [Table of contents](#table-of-contents)
  - [Integration](#integration)
    - [Init LogtoClient](#init-logtoclient)
    - [Implement the sign-in route](#implement-the-sign-in-route)
    - [Implement the callback route](#implement-the-callback-route)
    - [Implement the home page](#implement-the-home-page)
    - [Implement the sign-out route](#implement-the-sign-out-route)
    - [Checkpoint: Test your application](#checkpoint-test-your-application)
  - [Scopes and claims](#scopes-and-claims)
  - [Resources](#resources)

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

## Scopes and claims

Both of "scope" and "claim" are terms from the OAuth 2.0 and OpenID Connect (OIDC) specifications. In OIDC, there are some optional [scopes and claims conventions](https://openid.net/specs/openid-connect-core-1_0.html#Claims) to follow. Logto uses these conventions to define the scopes and claims for the ID token.

In short, when you request a scope, you will get the corresponding claims in the ID token. For example, if you request the `email` scope, you will get the `email` and `email_verified` claims in the ID token.

By default, Logto SDK requests `openid`, `profile`, ...

For types ...

## Resources
