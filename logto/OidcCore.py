import hashlib
from typing import Any, Optional
import aiohttp
import random
from jwt import PyJWKClient
import jwt
from pydantic import BaseModel, ConfigDict
from logto.LogtoException import LogtoException
from logto.utilities import removeFalsyKeys, urlsafeEncode

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

class TokenResponse(BaseModel):
  access_token: str
  token_type: str
  expires_in: int
  refresh_token: Optional[str] = None
  id_token: Optional[str] = None

class UserIdentity(BaseModel):
  userId: str
  details: Optional[dict[str, Any]] = None

class UserInfoResponse(BaseModel):
  sub: str
  name: Optional[str] = None
  username: Optional[str] = None
  picture: Optional[str] = None
  email: Optional[str] = None
  email_verified: Optional[bool] = None
  phone_number: Optional[str] = None
  phone_number_verified: Optional[bool] = None
  custom_data: Any = None
  identities: Optional[dict[str, UserIdentity]] = None

class OidcCore:
  defaultScopes: list[str] = ['openid', 'offline_access', 'profile']

  def __init__(self, metadata: OidcProviderMetadata) -> None:
    """
    Initialize the OIDC core with the provider metadata. You can use the
    `getProviderMetadata` method to fetch the provider metadata from the
    discovery URL.
    """
    self.metadata = metadata
    self.jwksClient = PyJWKClient(metadata.jwks_uri, headers={'user-agent': '@logto/python', 'accept': '*/*'})

  def generateState() -> str:
    """
    Generate a random string (32 bytes) for the state parameter.
    """
    return urlsafeEncode(random.randbytes(32))
  
  def generateCodeVerifier() -> str:
    """
    Generate a random code verifier string (32 bytes) for PKCE.

    See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.1
    """
    return urlsafeEncode(random.randbytes(32))
  
  def generateCodeChallenge(codeVerifier: str) -> str:
    """
    Generate a code challenge string for the given code verifier string.

    See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.2
    """
    return urlsafeEncode(hashlib.sha256(codeVerifier.encode('ascii')).digest())

  def decodeIdToken(idToken: str) -> IdTokenClaims:
    """
    Decode the ID Token and return the claims without verifying the signature.
    """
    return IdTokenClaims(**jwt.decode(idToken, options={'verify_signature': False}))

  def decodeAccessToken(accessToken: str) -> AccessTokenClaims:
    """
    Decode the access token and return the claims without verifying the signature.
    """
    return AccessTokenClaims(**jwt.decode(accessToken, options={'verify_signature': False}))
  
  async def getProviderMetadata(discoveryUrl: str) -> OidcProviderMetadata:
    """
    Fetch the provider metadata from the discovery URL.
    """
    async with aiohttp.ClientSession() as session:
      async with session.get(discoveryUrl) as resp:
        json = await resp.json()
        return OidcProviderMetadata(**json)

  async def fetchTokenByCode(self, clientId: str, clientSecret: str | None, redirectUri: str, code: str, codeVerifier: str) -> TokenResponse:
    """
    Fetch the token from the token endpoint using the authorization code.
    """
    tokenEndpoint = self.metadata.token_endpoint
    async with aiohttp.ClientSession() as session:
      async with session.post(tokenEndpoint, data={
        'grant_type': 'authorization_code',
        'client_id': clientId,
        'client_secret': clientSecret,
        'redirect_uri': redirectUri,
        'code': code,
        'code_verifier': codeVerifier,
      }) as resp:
        if resp.status != 200:
          raise LogtoException(await resp.text())

        json = await resp.json()
        return TokenResponse(**json)

  async def fetchTokenByRefreshToken(self, clientId: str, clientSecret: str | None, refreshToken: str, resource: str = '') -> TokenResponse:
    """
    Fetch the token from the token endpoint using the refresh token.
    """
    tokenEndpoint = self.metadata.token_endpoint
    async with aiohttp.ClientSession() as session:
      async with session.post(tokenEndpoint, data=removeFalsyKeys({
        'grant_type': 'refresh_token',
        'client_id': clientId,
        'client_secret': clientSecret,
        'refresh_token': refreshToken,
        'resource': resource,
      })) as resp:
        if resp.status != 200:
          raise LogtoException(await resp.text())

        json = await resp.json()
        return TokenResponse(**json)
      
  def verifyIdToken(self, idToken: str, clientId: str) -> None:
    """
    Verify the ID Token, throw an exception if the verification fails.
    """
    issuer = self.metadata.issuer
    signing_key = self.jwksClient.get_signing_key_from_jwt(idToken)
    jwt.decode(
      idToken,
      signing_key.key,
      algorithms=['RS256', 'PS256', 'ES256', 'ES384', 'ES512'],
      audience=clientId,
      issuer=issuer,
    )

  async def fetchUserInfo(self, accessToken: str) -> UserInfoResponse:
    """
    Fetch the user info from the OpenID Connect UserInfo endpoint.
    """
    userInfoEndpoint = self.metadata.userinfo_endpoint
    async with aiohttp.ClientSession() as session:
      async with session.get(userInfoEndpoint, headers={'Authorization': f'Bearer {accessToken}'}) as resp:
        if resp.status != 200:
          raise LogtoException(await resp.text())

        json = await resp.json()
        return UserInfoResponse(**json)
