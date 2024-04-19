import os

# A secret key for the Flask app, used for session management
APP_SECRET_KEY = (
    os.getenv("APP_SECRET_KEY") or b"1234567890abcdef"
)  # Replace with your own secret key

LOGTO_ENDPOINT = os.getenv("LOGTO_ENDPOINT") or "replace-with-your-logto-endpoint"
LOGTO_APP_ID = os.getenv("LOGTO_APP_ID") or "replace-with-your-app-id"
LOGTO_APP_SECRET = os.getenv("LOGTO_APP_SECRET") or "replace-with-your-app-secret"
LOGTO_REDIRECT_URI = os.getenv("LOGTO_REDIRECT_URI") or "replace-with-your-redirect-uri"
LOGTO_POST_LOGOUT_REDIRECT_URI = (
    os.getenv("LOGTO_POST_LOGOUT_REDIRECT_URI")
    or "replace-with-your-post-logout-redirect-uri"
)
