from flask import session
from logto import LogtoClient, LogtoConfig, Storage, UserInfoScope
from typing import Union
from samples.config import LOGTO_APP_ID, LOGTO_APP_SECRET, LOGTO_ENDPOINT


# Custom session storage class for Logto integration with Flask
class SessionStorage(Storage):
    def get(self, key: str) -> Union[str, None]:
        # Retrieve a value from Flask session storage
        return session.get(key, None)

    def set(self, key: str, value: Union[str, None]) -> None:
        # Set a value in Flask session storage
        session[key] = value

    def delete(self, key: str) -> None:
        # Delete a value from Flask session storage
        session.pop(key, None)


# Logto client initialization
client = LogtoClient(
    LogtoConfig(
        endpoint=LOGTO_ENDPOINT,
        appId=LOGTO_APP_ID,
        appSecret=LOGTO_APP_SECRET,
        scopes=[
            UserInfoScope.email,
            UserInfoScope.organizations,
            UserInfoScope.organization_roles,
            UserInfoScope.custom_data,
        ],  # Update scopes as needed
    ),
    storage=SessionStorage(),
)
