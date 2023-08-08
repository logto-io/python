from typing import Optional
from pydantic import BaseModel, ConfigDict

class OidcProviderMetadata(BaseModel):
  """
  The OpenID Connect Discovery response object.

  See https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata
  """
  issuer: str
  authorization_endpoint: str
  token_endpoint: str
  userinfo_endpoint: str # This is actually "RECOMMENDED" but Logto requires it
  jwks_uri: str
  registration_endpoint: Optional[str] = None
  scopes_supported: list[str] = []
  response_types_supported: list[str]
  response_modes_supported: list[str] = []
  grant_types_supported: list[str] = []
  acr_values_supported: list[str] = []
  subject_types_supported: list[str]
  id_token_signing_alg_values_supported: list[str]
  id_token_encryption_alg_values_supported: list[str] = []
  id_token_encryption_enc_values_supported: list[str] = []
  userinfo_signing_alg_values_supported: list[str] = []
  userinfo_encryption_alg_values_supported: list[str] = []
  userinfo_encryption_enc_values_supported: list[str] = []
  request_object_signing_alg_values_supported: list[str] = []
  request_object_encryption_alg_values_supported: list[str] = []
  request_object_encryption_enc_values_supported: list[str] = []
  token_endpoint_auth_methods_supported: list[str] = []
  token_endpoint_auth_signing_alg_values_supported: list[str] = []
  display_values_supported: list[str] = []
  claim_types_supported: list[str] = []
  claims_supported: list[str] = []
  service_documentation: Optional[str] = None
  claims_locales_supported: list[str] = []
  ui_locales_supported: list[str] = []
  claims_parameter_supported: bool = False
  request_parameter_supported: bool = False
  request_uri_parameter_supported: bool = True
  require_request_uri_registration: bool = False
  op_policy_uri: Optional[str] = None
  op_tos_uri: Optional[str] = None
  end_session_endpoint: Optional[str] = None
  code_challenge_methods_supported: list[str] = []

class IdTokenClaims(BaseModel):
  """
  The ID token claims object.
  
  To access the extra claims, use `__pydantic_extra__`. See
  https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.
  """

  model_config = ConfigDict(extra='allow')

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
  The audience that the token is intended for, which is the client ID or the resource
  indicator.
  """
  exp: int
  """
  The expiration time of the token (in seconds).
  """
  iat: int
  """
  The time at which the token was issued (in seconds).
  """
  at_hash: Optional[str] = None
  name: Optional[str] = None
  username: Optional[str] = None
  picture: Optional[str] = None
  email: Optional[str] = None
  email_verified: Optional[bool] = None
  phone_number: Optional[str] = None
  phone_number_verified: Optional[bool] = None

class AccessTokenClaims(BaseModel):
  """
  The access token claims object.
  
  To access the extra claims, use `__pydantic_extra__`. See
  https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.
  """

  model_config = ConfigDict(extra='allow')

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
  The audience that the token is intended for, which is the client ID or the resource
  indicator.
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
