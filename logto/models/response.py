from typing import Any, Optional, Dict, List
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    The response model from the token endpoint.
    """

    access_token: str
    """
    The access token string.
    """
    token_type: str
    """
    The token type string, should be "Bearer".
    """
    expires_in: int
    """
    The expiration time of the access token (in seconds).
    """
    refresh_token: Optional[str] = None
    """
    The refresh token string.
    """
    id_token: Optional[str] = None
    """
    The ID token string.
    """


class UserIdentity(BaseModel):
    """
    The user identity model.
    """

    userId: str
    """
    The user ID of the target identity.
    """
    details: Optional[Dict[str, Any]] = None
    """
    The details of the target identity, can be any JSON object.
    """


class UserInfoResponse(BaseModel):
    """
    The response model from the user info endpoint.
    """

    sub: str
    """
    The subject identifier for whom the token is intended (user ID).
    """
    name: Optional[str] = None
    """
    The full name of the user.
    """
    username: Optional[str] = None
    """
    The username of the user.
    """
    picture: Optional[str] = None
    """
    The profile picture URL of the user.
    """
    email: Optional[str] = None
    """
    The email address of the user.
    """
    email_verified: Optional[bool] = None
    """
    Whether the email address is verified.
    """
    phone_number: Optional[str] = None
    """
    The phone number of the user.
    """
    phone_number_verified: Optional[bool] = None
    """
    Whether the phone number is verified.
    """
    custom_data: Any = None
    """
    The custom data of the user, can be any JSON object.
    """
    identities: Optional[Dict[str, UserIdentity]] = None
    """
    The identities of the user, can be a dictionary of key-value pairs, where the key is
    the identity type and the value is the `UserIdentity` object.
    """
    organizations: Optional[List[str]] = None
    """The organization IDs that the user has membership."""
    organization_roles: Optional[List[str]] = None
    """
    The organization roles that the user has.
    Each role is in the format of `<organization_id>:<role_name>`.
    """
