from functools import wraps

from flask import g, jsonify, redirect
from samples.client import client


def authenticated(shouldRedirect: bool = False, fetchUserInfo: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if client.isAuthenticated() is False:
                if shouldRedirect:
                    return redirect("/sign-in")
                return jsonify({"error": "Not authenticated"}), 401

            # Store user info in Flask application context
            g.user = (
                await client.fetchUserInfo()
                if fetchUserInfo
                else client.getIdTokenClaims()
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
