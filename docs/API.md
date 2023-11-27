# Logto Python SDK API reference

* [logto](#logto)
* [logto.LogtoException](#logto.LogtoException)
  * [LogtoException](#logto.LogtoException.LogtoException)
* [logto.models.oidc](#logto.models.oidc)
  * [OidcProviderMetadata](#logto.models.oidc.OidcProviderMetadata)
  * [Scope](#logto.models.oidc.Scope)
  * [UserInfoScope](#logto.models.oidc.UserInfoScope)
  * [IdTokenClaims](#logto.models.oidc.IdTokenClaims)
  * [ReservedResource](#logto.models.oidc.ReservedResource)
  * [AccessTokenClaims](#logto.models.oidc.AccessTokenClaims)
* [logto.models.response](#logto.models.response)
  * [TokenResponse](#logto.models.response.TokenResponse)
  * [UserIdentity](#logto.models.response.UserIdentity)
  * [UserInfoResponse](#logto.models.response.UserInfoResponse)
* [logto.LogtoClient](#logto.LogtoClient)
  * [LogtoConfig](#logto.LogtoClient.LogtoConfig)
  * [SignInSession](#logto.LogtoClient.SignInSession)
  * [AccessToken](#logto.LogtoClient.AccessToken)
  * [AccessTokenMap](#logto.LogtoClient.AccessTokenMap)
  * [InteractionMode](#logto.LogtoClient.InteractionMode)
  * [LogtoClient](#logto.LogtoClient.LogtoClient)
* [logto.OidcCore](#logto.OidcCore)
  * [OidcCore](#logto.OidcCore.OidcCore)
* [logto.utilities](#logto.utilities)
  * [urlsafeEncode](#logto.utilities.urlsafeEncode)
  * [removeFalsyKeys](#logto.utilities.removeFalsyKeys)
  * [OrganizationUrnPrefix](#logto.utilities.OrganizationUrnPrefix)
  * [buildOrganizationUrn](#logto.utilities.buildOrganizationUrn)
* [logto.utilities.test](#logto.utilities.test)
* [logto.Storage](#logto.Storage)
  * [PersistKey](#logto.Storage.PersistKey)
  * [Storage](#logto.Storage.Storage)
  * [MemoryStorage](#logto.Storage.MemoryStorage)

<a id="logto"></a>

# logto

<a id="logto.LogtoException"></a>

# logto.LogtoException

<a id="logto.LogtoException.LogtoException"></a>

## LogtoException

```python
class LogtoException(Exception)
```

The exception class to identify the exceptions from the Logto client.

<a id="logto.models.oidc"></a>

# logto.models.oidc

<a id="logto.models.oidc.OidcProviderMetadata"></a>

## OidcProviderMetadata

```python
class OidcProviderMetadata(BaseModel)
```

The OpenID Connect Discovery response object.

See https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata

<a id="logto.models.oidc.OidcProviderMetadata.userinfo_endpoint"></a>

#### userinfo\_endpoint

This is actually "RECOMMENDED" but Logto requires it

<a id="logto.models.oidc.Scope"></a>

## Scope

```python
class Scope(Enum)
```

The scope base class for determining the scope type.

<a id="logto.models.oidc.UserInfoScope"></a>

## UserInfoScope

```python
class UserInfoScope(Scope)
```

The available scopes for the userinfo endpoint and the ID token claims.

<a id="logto.models.oidc.UserInfoScope.openid"></a>

#### openid

The preserved scope for OpenID Connect. It maps to the `sub` claim.

<a id="logto.models.oidc.UserInfoScope.profile"></a>

#### profile

The scope for the basic profile. It maps to the `name`, `username`, `picture` claims.

<a id="logto.models.oidc.UserInfoScope.email"></a>

#### email

The scope for the email address. It maps to the `email`, `email_verified` claims.

<a id="logto.models.oidc.UserInfoScope.phone"></a>

#### phone

The scope for the phone number. It maps to the `phone_number`, `phone_number_verified` claims.

<a id="logto.models.oidc.UserInfoScope.customData"></a>

#### customData

The scope for the custom data. It maps to the `custom_data` claim.

Note that the custom data is not included in the ID token by default. You need to
use `fetchUserInfo()` to get the custom data.

<a id="logto.models.oidc.UserInfoScope.identities"></a>

#### identities

The scope for the identities. It maps to the `identities` claim.

Note that the identities are not included in the ID token by default. You need to
use `fetchUserInfo()` to get the identities.

<a id="logto.models.oidc.UserInfoScope.organizations"></a>

#### organizations

Scope for user's organization IDs and perform organization token grant per [RFC 0001](https://github.com/logto-io/rfcs).

<a id="logto.models.oidc.UserInfoScope.organization_roles"></a>

#### organization\_roles

Scope for user's organization roles per [RFC 0001](https://github.com/logto-io/rfcs).

<a id="logto.models.oidc.IdTokenClaims"></a>

## IdTokenClaims

```python
class IdTokenClaims(BaseModel)
```

The ID token claims object.

To access the extra claims, use `__pydantic_extra__`. See
https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.

<a id="logto.models.oidc.IdTokenClaims.iss"></a>

#### iss

The issuer identifier for whom issued the token.

<a id="logto.models.oidc.IdTokenClaims.sub"></a>

#### sub

The subject identifier for whom the token is intended (user ID).

<a id="logto.models.oidc.IdTokenClaims.aud"></a>

#### aud

The audience that the token is intended for, which is the client ID.

<a id="logto.models.oidc.IdTokenClaims.exp"></a>

#### exp

The expiration time of the token (in seconds).

<a id="logto.models.oidc.IdTokenClaims.iat"></a>

#### iat

The time at which the token was issued (in seconds).

<a id="logto.models.oidc.IdTokenClaims.name"></a>

#### name

The user's full name.

<a id="logto.models.oidc.IdTokenClaims.username"></a>

#### username

The user's username.

<a id="logto.models.oidc.IdTokenClaims.picture"></a>

#### picture

The user's profile picture URL.

<a id="logto.models.oidc.IdTokenClaims.email"></a>

#### email

The user's email address.

<a id="logto.models.oidc.IdTokenClaims.email_verified"></a>

#### email\_verified

Whether the user's email address is verified.

<a id="logto.models.oidc.IdTokenClaims.phone_number"></a>

#### phone\_number

The user's phone number.

<a id="logto.models.oidc.IdTokenClaims.phone_number_verified"></a>

#### phone\_number\_verified

Whether the user's phone number is verified.

<a id="logto.models.oidc.IdTokenClaims.organizations"></a>

#### organizations

The organization IDs that the user has membership.

<a id="logto.models.oidc.IdTokenClaims.organization_roles"></a>

#### organization\_roles

The organization roles that the user has.
Each role is in the format of `<organization_id>:<role_name>`.

<a id="logto.models.oidc.ReservedResource"></a>

## ReservedResource

```python
class ReservedResource(Enum)
```

Resources that reserved by Logto, which cannot be defined by users.

<a id="logto.models.oidc.ReservedResource.organizations"></a>

#### organizations

The resource for organization template per [RFC 0001](https://github.com/logto-io/rfcs).

<a id="logto.models.oidc.AccessTokenClaims"></a>

## AccessTokenClaims

```python
class AccessTokenClaims(BaseModel)
```

The access token claims object.

To access the extra claims, use `__pydantic_extra__`. See
https://docs.pydantic.dev/latest/usage/models/#extra-fields for more information.

<a id="logto.models.oidc.AccessTokenClaims.iss"></a>

#### iss

The issuer identifier for whom issued the token.

<a id="logto.models.oidc.AccessTokenClaims.sub"></a>

#### sub

The subject identifier for whom the token is intended (user ID).

<a id="logto.models.oidc.AccessTokenClaims.aud"></a>

#### aud

The audience that the token is intended for, which may be one of the following:
- Client ID
- Resource indicator
- Logto organization URN (`urn:logto:organization:<organization_id>`)

<a id="logto.models.oidc.AccessTokenClaims.exp"></a>

#### exp

The expiration time of the token (in seconds).

<a id="logto.models.oidc.AccessTokenClaims.iat"></a>

#### iat

The time at which the token was issued (in seconds).

<a id="logto.models.oidc.AccessTokenClaims.scope"></a>

#### scope

The scopes that the token is granted for.

<a id="logto.models.oidc.AccessTokenClaims.client_id"></a>

#### client\_id

The client ID that the token is granted for. Useful when the client ID is not
included in the `aud` claim.

<a id="logto.models.response"></a>

# logto.models.response

<a id="logto.models.response.TokenResponse"></a>

## TokenResponse

```python
class TokenResponse(BaseModel)
```

The response model from the token endpoint.

<a id="logto.models.response.TokenResponse.access_token"></a>

#### access\_token

The access token string.

<a id="logto.models.response.TokenResponse.token_type"></a>

#### token\_type

The token type string, should be "Bearer".

<a id="logto.models.response.TokenResponse.expires_in"></a>

#### expires\_in

The expiration time of the access token (in seconds).

<a id="logto.models.response.TokenResponse.refresh_token"></a>

#### refresh\_token

The refresh token string.

<a id="logto.models.response.TokenResponse.id_token"></a>

#### id\_token

The ID token string.

<a id="logto.models.response.UserIdentity"></a>

## UserIdentity

```python
class UserIdentity(BaseModel)
```

The user identity model.

<a id="logto.models.response.UserIdentity.userId"></a>

#### userId

The user ID of the target identity.

<a id="logto.models.response.UserIdentity.details"></a>

#### details

The details of the target identity, can be any JSON object.

<a id="logto.models.response.UserInfoResponse"></a>

## UserInfoResponse

```python
class UserInfoResponse(BaseModel)
```

The response model from the user info endpoint.

<a id="logto.models.response.UserInfoResponse.sub"></a>

#### sub

The subject identifier for whom the token is intended (user ID).

<a id="logto.models.response.UserInfoResponse.name"></a>

#### name

The full name of the user.

<a id="logto.models.response.UserInfoResponse.username"></a>

#### username

The username of the user.

<a id="logto.models.response.UserInfoResponse.picture"></a>

#### picture

The profile picture URL of the user.

<a id="logto.models.response.UserInfoResponse.email"></a>

#### email

The email address of the user.

<a id="logto.models.response.UserInfoResponse.email_verified"></a>

#### email\_verified

Whether the email address is verified.

<a id="logto.models.response.UserInfoResponse.phone_number"></a>

#### phone\_number

The phone number of the user.

<a id="logto.models.response.UserInfoResponse.phone_number_verified"></a>

#### phone\_number\_verified

Whether the phone number is verified.

<a id="logto.models.response.UserInfoResponse.custom_data"></a>

#### custom\_data

The custom data of the user, can be any JSON object.

<a id="logto.models.response.UserInfoResponse.identities"></a>

#### identities

The identities of the user, can be a dictionary of key-value pairs, where the key is
the identity type and the value is the `UserIdentity` object.

<a id="logto.models.response.UserInfoResponse.organizations"></a>

#### organizations

The organization IDs that the user has membership.

<a id="logto.models.response.UserInfoResponse.organization_roles"></a>

#### organization\_roles

The organization roles that the user has.
Each role is in the format of `<organization_id>:<role_name>`.

<a id="logto.LogtoClient"></a>

# logto.LogtoClient

The Logto client class and the related models.

<a id="logto.LogtoClient.LogtoConfig"></a>

## LogtoConfig

```python
class LogtoConfig(BaseModel)
```

The configuration object for the Logto client.

<a id="logto.LogtoClient.LogtoConfig.endpoint"></a>

#### endpoint

The endpoint for the Logto server, you can get it from the integration guide
or the team settings page of the Logto Console.

Example:
https://foo.logto.app

<a id="logto.LogtoClient.LogtoConfig.appId"></a>

#### appId

The client ID of your application, you can get it from the integration guide
or the application details page of the Logto Console.

<a id="logto.LogtoClient.LogtoConfig.appSecret"></a>

#### appSecret

The client secret of your application, you can get it from the integration guide
or the application details page of the Logto Console.

<a id="logto.LogtoClient.LogtoConfig.prompt"></a>

#### prompt

The prompt parameter for the OpenID Connect authorization request.

- If the value is `consent`, the user will be able to reuse the existing consent
without being prompted for sign-in again.
- If the value is `login`, the user will be prompted for sign-in again anyway. Note
there will be no Refresh Token returned in this case.

<a id="logto.LogtoClient.LogtoConfig.resources"></a>

#### resources

The API resources that your application needs to access. You can specify multiple
resources by providing an array of strings.

See https://docs.logto.io/docs/recipes/rbac/ to learn more about how to use role-based
access control (RBAC) to protect API resources.

<a id="logto.LogtoClient.LogtoConfig.scopes"></a>

#### scopes

The scopes (permissions) that your application needs to access.
Scopes that will be added by default: `openid`, `offline_access` and `profile`.

If resources are specified, scopes will be applied to every resource.

See https://docs.logto.io/docs/recipes/integrate-logto/vanilla-js/#fetch-user-information
for more information of available scopes for user information.

<a id="logto.LogtoClient.SignInSession"></a>

## SignInSession

```python
class SignInSession(BaseModel)
```

The sign-in session that stores the information for the sign-in callback.
Should be stored before redirecting the user to Logto.

<a id="logto.LogtoClient.SignInSession.redirectUri"></a>

#### redirectUri

The redirect URI for the current sign-in session.

<a id="logto.LogtoClient.SignInSession.codeVerifier"></a>

#### codeVerifier

The code verifier of Proof Key for Code Exchange (PKCE).

<a id="logto.LogtoClient.SignInSession.state"></a>

#### state

The state for OAuth 2.0 authorization request.

<a id="logto.LogtoClient.AccessToken"></a>

## AccessToken

```python
class AccessToken(BaseModel)
```

The access token class for a resource.

<a id="logto.LogtoClient.AccessToken.token"></a>

#### token

The access token string.

<a id="logto.LogtoClient.AccessToken.expiresAt"></a>

#### expiresAt

The timestamp (in seconds) when the access token will expire.
Note this is not the expiration time of the access token itself, but the
expiration time of the access token cache.

<a id="logto.LogtoClient.AccessTokenMap"></a>

## AccessTokenMap

```python
class AccessTokenMap(BaseModel)
```

The access token map that maps the resource to the access token for that resource.

If resource is an empty string, it means the access token is for UserInfo endpoint
or the default resource.

<a id="logto.LogtoClient.InteractionMode"></a>

#### InteractionMode

The interaction mode for the sign-in request. Note this is not a part of the OIDC
specification, but a Logto extension.

<a id="logto.LogtoClient.LogtoClient"></a>

## LogtoClient

```python
class LogtoClient()
```

The main class of the Logto client. You should create an instance of this class
and use it to sign in, sign out, get access token, etc.

<a id="logto.LogtoClient.LogtoClient.getOidcCore"></a>

#### getOidcCore

```python
async def getOidcCore() -> OidcCore
```

Get the OIDC core object. You can use it to get the provider metadata, verify
the ID token, fetch tokens by code or refresh token, etc.

<a id="logto.LogtoClient.LogtoClient.signIn"></a>

#### signIn

```python
async def signIn(redirectUri: str,
                 interactionMode: Optional[InteractionMode] = None) -> str
```

Returns the sign-in URL for the given redirect URI. You should redirect the user
to the returned URL to sign in.

By specifying the interaction mode, you can control whether the user will be
prompted for sign-in or sign-up on the first screen. If the interaction mode is
not specified, the default one will be used.

Example:
  ```python
  return redirect(await client.signIn('https://example.com/callback'))
  ```

<a id="logto.LogtoClient.LogtoClient.signOut"></a>

#### signOut

```python
async def signOut(postLogoutRedirectUri: Optional[str] = None) -> str
```

Returns the sign-out URL for the given post-logout redirect URI. You should
redirect the user to the returned URL to sign out.

If the post-logout redirect URI is not provided, the Logto default post-logout
redirect URI will be used.

Note:
  If the OpenID Connect server does not support the end session endpoint
  (i.e. OpenID Connect RP-Initiated Logout), the function will throw an
  exception. Logto supports the end session endpoint.

Example:
  ```python
  return redirect(await client.signOut('https://example.com'))
  ```

<a id="logto.LogtoClient.LogtoClient.handleSignInCallback"></a>

#### handleSignInCallback

```python
async def handleSignInCallback(callbackUri: str) -> None
```

Handle the sign-in callback from the Logto server. This method should be called
in the callback route handler of your application.

<a id="logto.LogtoClient.LogtoClient.getAccessToken"></a>

#### getAccessToken

```python
async def getAccessToken(resource: str = "") -> Optional[str]
```

Get the access token for the given resource. If the access token is expired,
it will be refreshed automatically. If no refresh token is found, None will
be returned.

<a id="logto.LogtoClient.LogtoClient.getOrganizationToken"></a>

#### getOrganizationToken

```python
async def getOrganizationToken(organizationId: str) -> Optional[str]
```

Get the access token for the given organization ID. If the access token is expired,
it will be refreshed automatically. If no refresh token is found, None will
be returned.

<a id="logto.LogtoClient.LogtoClient.getAccessTokenClaims"></a>

#### getAccessTokenClaims

```python
async def getAccessTokenClaims(resource: str = "") -> AccessTokenClaims
```

Get the claims in the access token for the given resource. If the access token
is expired, it will be refreshed automatically. If it's unable to refresh the
access token, an exception will be thrown.

<a id="logto.LogtoClient.LogtoClient.getOrganizationTokenClaims"></a>

#### getOrganizationTokenClaims

```python
async def getOrganizationTokenClaims(organizationId: str) -> AccessTokenClaims
```

Get the claims in the access token for the given organization ID. If the access token
is expired, it will be refreshed automatically. If it's unable to refresh the
access token, an exception will be thrown.

<a id="logto.LogtoClient.LogtoClient.getIdToken"></a>

#### getIdToken

```python
def getIdToken() -> Optional[str]
```

Get the ID Token string. If you need to get the claims in the ID Token, use
`getIdTokenClaims` instead.

<a id="logto.LogtoClient.LogtoClient.getIdTokenClaims"></a>

#### getIdTokenClaims

```python
def getIdTokenClaims() -> IdTokenClaims
```

Get the claims in the ID Token. If the ID Token does not exist, an exception
will be thrown.

<a id="logto.LogtoClient.LogtoClient.getRefreshToken"></a>

#### getRefreshToken

```python
def getRefreshToken() -> Optional[str]
```

Get the refresh token string.

<a id="logto.LogtoClient.LogtoClient.isAuthenticated"></a>

#### isAuthenticated

```python
def isAuthenticated() -> bool
```

Check if the user is authenticated by checking if the ID Token exists.

<a id="logto.LogtoClient.LogtoClient.fetchUserInfo"></a>

#### fetchUserInfo

```python
async def fetchUserInfo() -> UserInfoResponse
```

Fetch the user information from the UserInfo endpoint. If the access token
is expired, it will be refreshed automatically.

<a id="logto.OidcCore"></a>

# logto.OidcCore

The core OIDC functions for the Logto client. Provider-agonistic functions
are implemented as static methods, while other functions are implemented as
instance methods.

<a id="logto.OidcCore.OidcCore"></a>

## OidcCore

```python
class OidcCore()
```

<a id="logto.OidcCore.OidcCore.__init__"></a>

#### \_\_init\_\_

```python
def __init__(metadata: OidcProviderMetadata) -> None
```

Initialize the OIDC core with the provider metadata. You can use the
`getProviderMetadata` method to fetch the provider metadata from the
discovery URL.

<a id="logto.OidcCore.OidcCore.generateState"></a>

#### generateState

```python
def generateState() -> str
```

Generate a random string (32 bytes) for the state parameter.

<a id="logto.OidcCore.OidcCore.generateCodeVerifier"></a>

#### generateCodeVerifier

```python
def generateCodeVerifier() -> str
```

Generate a random code verifier string (32 bytes) for PKCE.

See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.1

<a id="logto.OidcCore.OidcCore.generateCodeChallenge"></a>

#### generateCodeChallenge

```python
def generateCodeChallenge(codeVerifier: str) -> str
```

Generate a code challenge string for the given code verifier string.

See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.2

<a id="logto.OidcCore.OidcCore.decodeIdToken"></a>

#### decodeIdToken

```python
def decodeIdToken(idToken: str) -> IdTokenClaims
```

Decode the ID Token and return the claims without verifying the signature.

<a id="logto.OidcCore.OidcCore.decodeAccessToken"></a>

#### decodeAccessToken

```python
def decodeAccessToken(accessToken: str) -> AccessTokenClaims
```

Decode the access token and return the claims without verifying the signature.

<a id="logto.OidcCore.OidcCore.getProviderMetadata"></a>

#### getProviderMetadata

```python
async def getProviderMetadata(discoveryUrl: str) -> OidcProviderMetadata
```

Fetch the provider metadata from the discovery URL.

<a id="logto.OidcCore.OidcCore.fetchTokenByCode"></a>

#### fetchTokenByCode

```python
async def fetchTokenByCode(clientId: str, clientSecret: Optional[str],
                           redirectUri: str, code: str,
                           codeVerifier: str) -> TokenResponse
```

Fetch the token from the token endpoint using the authorization code.

<a id="logto.OidcCore.OidcCore.fetchTokenByRefreshToken"></a>

#### fetchTokenByRefreshToken

```python
async def fetchTokenByRefreshToken(clientId: str,
                                   clientSecret: Optional[str],
                                   refreshToken: str,
                                   resource: str = "") -> TokenResponse
```

Fetch the token from the token endpoint using the refresh token.

If the resource is an organization URN, the organization ID will be extracted
and used as the `organization_id` parameter.

<a id="logto.OidcCore.OidcCore.verifyIdToken"></a>

#### verifyIdToken

```python
def verifyIdToken(idToken: str, clientId: str) -> None
```

Verify the ID Token signature and its issuer and client ID, throw an exception
if the verification fails.

<a id="logto.OidcCore.OidcCore.fetchUserInfo"></a>

#### fetchUserInfo

```python
async def fetchUserInfo(accessToken: str) -> UserInfoResponse
```

Fetch the user info from the OpenID Connect UserInfo endpoint.

See: https://openid.net/specs/openid-connect-core-1_0.html#UserInfo

<a id="logto.utilities"></a>

# logto.utilities

<a id="logto.utilities.urlsafeEncode"></a>

#### urlsafeEncode

```python
def urlsafeEncode(data: bytes) -> str
```

Encode the given bytes to a URL-safe string.

<a id="logto.utilities.removeFalsyKeys"></a>

#### removeFalsyKeys

```python
def removeFalsyKeys(data: Dict[str, Any]) -> Dict[str, Any]
```

Remove keys with falsy values from the given dictionary.

<a id="logto.utilities.OrganizationUrnPrefix"></a>

#### OrganizationUrnPrefix

The prefix for Logto organization URNs.

<a id="logto.utilities.buildOrganizationUrn"></a>

#### buildOrganizationUrn

```python
def buildOrganizationUrn(organizationId: str) -> str
```

Build the organization URN from the organization ID.

Example:
```python
buildOrganizationUrn("1") # returns "urn:logto:organization:1"
```

<a id="logto.utilities.test"></a>

# logto.utilities.test

<a id="logto.Storage"></a>

# logto.Storage

Logto client storage abstract class and the default implementation.

<a id="logto.Storage.PersistKey"></a>

#### PersistKey

The keys literal for the persistent storage.

<a id="logto.Storage.Storage"></a>

## Storage

```python
class Storage(ABC)
```

The storage interface for the Logto client. Logto client will use this
interface to store and retrieve the logto session data.

Usually this should be implemented as a persistent storage, such as a
session or a database, since the page will be redirected to Logto and
then back to the original page.

<a id="logto.Storage.Storage.get"></a>

#### get

```python
@abstractmethod
def get(key: PersistKey) -> Optional[str]
```

Get the stored string for the given key, return None if not found.

<a id="logto.Storage.Storage.set"></a>

#### set

```python
@abstractmethod
def set(key: PersistKey, value: Optional[str]) -> None
```

Set the stored value (string or None) for the given key.

<a id="logto.Storage.MemoryStorage"></a>

## MemoryStorage

```python
class MemoryStorage(Storage)
```

The in-memory storage implementation for the Logto client. Note this should
only be used for testing, since the data will be lost after the page is
redirected.

See `Storage` for the interface.

