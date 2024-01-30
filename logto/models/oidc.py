from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict
import warnings


class OidcProviderMetadata(BaseModel):
    """
    The OpenID Connect Discovery response object.

    See https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata
    """

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str  # This is actually "RECOMMENDED" but Logto requires it
    jwks_uri: str
    registration_endpoint: Optional[str] = None
    scopes_supported: List[str] = []
    response_types_supported: List[str]
    response_modes_supported: List[str] = []
    grant_types_supported: List[str] = []
    acr_values_supported: List[str] = []
    subject_types_supported: List[str]
    id_token_signing_alg_values_supported: List[str]
    id_token_encryption_alg_values_supported: List[str] = []
    id_token_encryption_enc_values_supported: List[str] = []
    userinfo_signing_alg_values_supported: List[str] = []
    userinfo_encryption_alg_values_supported: List[str] = []
    userinfo_encryption_enc_values_supported: List[str] = []
    request_object_signing_alg_values_supported: List[str] = []
    request_object_encryption_alg_values_supported: List[str] = []
    request_object_encryption_enc_values_supported: List[str] = []
    token_endpoint_auth_methods_supported: List[str] = []
    token_endpoint_auth_signing_alg_values_supported: List[str] = []
    display_values_supported: List[str] = []
    claim_types_supported: List[str] = []
    claims_supported: List[str] = []
    service_documentation: Optional[str] = None
    claims_locales_supported: List[str] = []
    ui_locales_supported: List[str] = []
    claims_parameter_supported: bool = False
    request_parameter_supported: bool = False
    request_uri_parameter_supported: bool = True
    require_request_uri_registration: bool = False
    op_policy_uri: Optional[str] = None
    op_tos_uri: Optional[str] = None
    end_session_endpoint: Optional[str] = None
    code_challenge_methods_supported: List[str] = []


class Scope(Enum):
    """The scope base class for determining the scope type."""

    def __new__(cls, value: Any):
        member = object.__new__(cls)
        member._value_ = value
        return member

    @classmethod
    def _get_deprecated_member(cls, member):
        # _get_deprecated_member is a protect util method to get the deprecated member with warning.
        warnings.warn(f"{member.name} is deprecated.", DeprecationWarning, stacklevel=2)
        return member


class OAuthScope(Scope):
    offlineAccess = "offline_access"


class UserInfoScope(Scope):
    """
    The available scopes for the userinfo endpoint and the ID token claims.
    """

    openid = "openid"
    """The reserved scope for OpenID Connect. It maps to the `sub` claim."""
    profile = "profile"
    """The scope for the basic profile. It maps to the `name`, `username`, `picture` claims."""
    email = "email"
    """The scope for the email address. It maps to the `email`, `email_verified` claims."""
    phone = "phone"
    """The scope for the phone number. It maps to the `phone_number`, `phone_number_verified` claims."""
    customData = "custom_data"
    """
    DEPRECATED: use `custom_data` instead.

    The scope for the custom data. It maps to the `custom_data` claim.

    Note that the custom data is not included in the ID token by default. You need to
    use `fetchUserInfo()` to get the custom data.
    """
    custom_data = "custom_data"
    """
    The scope for the custom data. It maps to the `custom_data` claim.

    Note that the custom data is not included in the ID token by default. You need to
    use `fetchUserInfo()` to get the custom data.
    """
    identities = "identities"
    """
    The scope for the identities. It maps to the `identities` claim.

    Note that the identities are not included in the ID token by default. You need to
    use `fetchUserInfo()` to get the identities.
    """
    organizations = "urn:logto:scope:organizations"
    """
    Scope for user's organization IDs and perform organization token grant per [RFC 0001](https://github.com/logto-io/rfcs).

    To learn more about Logto Organizations, see https://docs.logto.io/docs/recipes/organizations/.
    """
    organization_roles = "urn:logto:scope:organization_roles"
    """
    Scope for user's organization roles per [RFC 0001](https://github.com/logto-io/rfcs).

    To learn more about Logto Organizations, see https://docs.logto.io/docs/recipes/organizations/.
    """

    @classmethod
    def _missing_(cls, value):
        """
        `_missing_` is a [built-in method](https://docs.python.org/3/library/enum.html#supported-sunder-names) to handle
        missing members, we overwrite it and throws a warning for deprecated members.

        In this way, we can both warn the users, keep the type checking working and make the deprecated value backward compatible.
        """
        if value == cls.customData.value:
            return cls._get_deprecated_member(cls.customData)
        return super()._missing_(value)


class IdTokenClaims(BaseModel):
    """
    The ID token claims object.

    To access the extra claims, use `__pydantic_extra__`. See
    https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.
    """

    model_config = ConfigDict(extra="allow")

    iss: str
    """The issuer identifier for whom issued the token."""
    sub: str
    """The subject identifier for whom the token is intended (user ID)."""
    aud: str
    """
    The audience that the token is intended for, which is the client ID.
    """
    exp: int
    """The expiration time of the token (in seconds)."""
    iat: int
    """The time at which the token was issued (in seconds)."""
    at_hash: Optional[str] = None
    name: Optional[str] = None
    """The user's full name."""
    username: Optional[str] = None
    """The user's username."""
    picture: Optional[str] = None
    """The user's profile picture URL."""
    email: Optional[str] = None
    """The user's email address."""
    email_verified: Optional[bool] = None
    """Whether the user's email address is verified."""
    phone_number: Optional[str] = None
    """The user's phone number."""
    phone_number_verified: Optional[bool] = None
    """Whether the user's phone number is verified."""
    organizations: Optional[List[str]] = None
    """The organization IDs that the user has membership."""
    organization_roles: Optional[List[str]] = None
    """
    The organization roles that the user has.
    Each role is in the format of `<organization_id>:<role_name>`.
    """


class ReservedResource(Enum):
    """Resources that reserved by Logto, which cannot be defined by users."""

    organizations = "urn:logto:resource:organizations"
    """The resource for organization template per [RFC 0001](https://github.com/logto-io/rfcs)."""


class AccessTokenClaims(BaseModel):
    """
    The access token claims object.

    To access the extra claims, use `__pydantic_extra__`. See
    https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.
    """

    model_config = ConfigDict(extra="allow")

    iss: str
    """
    The issuer identifier for whom issued the token.
    """
    sub: str
    """
    The subject identifier for whom the token is intended (user ID).
    """
    aud: str
    """
    The audience that the token is intended for, which may be one of the following:
    - Client ID
    - Resource indicator
    - Logto organization URN (`urn:logto:organization:<organization_id>`)
    """
    exp: int
    """
    The expiration time of the token (in seconds).
    """
    iat: int
    """
    The time at which the token was issued (in seconds).
    """
    scope: str
    """
    The scopes that the token is granted for.
    """
    client_id: Optional[str] = None
    """
    The client ID that the token is granted for. Useful when the client ID is not
    included in the `aud` claim.
    """
