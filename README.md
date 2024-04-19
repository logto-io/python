# Logto Python SDK

[![Logto](https://img.shields.io/badge/for-logto-7958ff)][Website]
[![Stable Version](https://img.shields.io/pypi/v/logto?label=stable)][PyPI Releases]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/logto)][PyPI]
[![PyPI - License](https://img.shields.io/pypi/l/logto)](https://github.com/logto-io/python)
[![Discord](https://img.shields.io/discord/965845662535147551?color=5865f2&logo=discord&label=discord)][Discord]

## Prerequisites

- Python 3.8 or higher
- A [Logto Cloud][Website] account or a self-hosted Logto
- A Logto traditional web application created

If you don't have the Logto application created, please follow the [⚡ Get started](https://docs.logto.io/docs/tutorials/get-started/) guide to create one.

## Installation
```bash
pip install logto # or `poetry add logto` or whatever you use
```

## Tutorial

See [tutorial](./docs/tutorial.md) for a quick start.

## API reference

See [API reference](./docs/api.md) for more details.

## Run the sample

There's a Flask sample in the [samples](./samples) directory. The sample has been tested with Python 3.8.17.

### Install dependencies

This repo uses [PDM](https://github.com/pdm-project/pdm) as the package manager. To install the dependencies, run the following command in the root directory of the repo (not in the `samples` directory):

```bash
pdm install
```

### Configure environment variables

To run the sample, you need to set the following environment variables:

```bash
APP_SECRET_KEY=your-secret-key # This is for Flask
LOGTO_ENDPOINT=http://your-logto-endpoint.com
LOGTO_APP_ID=your-logto-app-id
LOGTO_APP_SECRET=your-logto-app-secret
LOGTO_REDIRECT_URI=http://127.0.0.1:5000/sign-in-callback
LOGTO_POST_LOGOUT_REDIRECT_URI=http://127.0.0.1:5000/
```

Replace the values with your own.

For `LOGTO_REDIRECT_URI` and `LOGTO_POST_LOGOUT_REDIRECT_URI`, you should:

1. Go to your Logto Console and add the URIs to the application's settings accordingly.
2. Update the domain and port to match your local environment if necessary.

> [!Note]
> The sample project also support dotenv. You can create a `.env` file in the root directory of the sample project and add the environment variables there.

### Run the sample

In the root directory of the repo, run the following command:

```bash
pdm run flask
```

The script can be found in the `pyproject.toml` file.

### Fetch user information

Call `client.getIdTokenClaims()` to get the basic user info. For a more detailed user info, you can call `client.fetchUserInfo()`.

For details on fetching user info, see the [Get user information](https://docs.logto.io/sdk/python/#get-user-information).

### Route protection

You have many ways to accomplish this.

**Directly check the user's authentication status**

You can call `client.isAuthenticated()` to check if the user is authenticated and can proceed with the request.

**Use a decorator**

You can create a decorator like `@authenticated()` to protect your routes. A sample decorator can be found at [samples/authenticated.py](./samples/authenticated.py).

For instance, an API may throw a 401 error if the user is not authenticated:

```python
from flask import g, jsonify

@app.route("/api/protected")
@authenticated()
def protected():
    print(g.user) # The `@authenticated()` decorator sets the user object in the `g` object
    return jsonify({"message": "This is a protected route"})
```

Or, you can redirect the user to the sign-in page:

```python
from flask import g, jsonify

@app.route("/protected")
@authenticated(shouldRedirect=True)
def protected():
    return "This is a protected route"
```

See the [flask.py](./samples/flask.py) file for more details.

## Resources

- [Logto website][Website]
- [Logto documentation](https://docs.logto.io/)
- [Join Discord][Discord]

[Website]: https://logto.io/
[PyPI]: https://pypi.org/project/logto/
[PyPI Releases]: https://pypi.org/project/logto/#history
[Discord]: https://discord.gg/vRvwuwgpVX
