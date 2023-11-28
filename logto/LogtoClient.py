"""
The Logto client class and the related models.
"""

import time
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel
import urllib.parse

from .models.oidc import ReservedResource, Scope, UserInfoScope
from .Storage import MemoryStorage, Storage
from .LogtoException import LogtoException
from .OidcCore import (
    AccessTokenClaims,
    IdTokenClaims,
    OidcCore,
    TokenResponse,
    UserInfoResponse,
)
from .utilities import OrganizationUrnPrefix, buildOrganizationUrn, removeFalsyKeys


class LogtoConfig(BaseModel):
    """
    The configuration object for the Logto client.
    """

    endpoint: str
    """
    The endpoint for the Logto server, you can get it from the integration guide
    or the team settings page of the Logto Console.

    Example:
    https://foo.logto.app
    """

    appId: str
    """
    The client ID of your application, you can get it from the integration guide
    or the application details page of the Logto Console.
    """

    appSecret: Optional[str] = None
    """
    The client secret of your application, you can get it from the integration guide
    or the application details page of the Logto Console.
    """

    prompt: Literal["consent", "login"] = "consent"
    """
    The prompt parameter for the OpenID Connect authorization request.

    - If the value is `consent`, the user will be able to reuse the existing consent
    without being prompted for sign-in again.
    - If the value is `login`, the user will be prompted for sign-in again anyway. Note
    there will be no Refresh Token returned in this case.
    """

    resources: List[str] = []
    """
    The API resources that your application needs to access. You can specify multiple
    resources by providing an array of strings.

    See https://docs.logto.io/docs/recipes/rbac/ to learn more about how to use role-based
    access control (RBAC) to protect API resources.
    """

    scopes: List[Union[str, Scope]] = []
    """
    The scopes (permissions) that your application needs to access.
    Scopes that will be added by default: `openid`, `offline_access` and `profile`.

    If resources are specified, scopes will be applied to every resource.

    See https://docs.logto.io/docs/recipes/integrate-logto/vanilla-js/#fetch-user-information
    for more information of available scopes for user information.
    """


class SignInSession(BaseModel):
    """
    The sign-in session that stores the information for the sign-in callback.
    Should be stored before redirecting the user to Logto.
    """

    redirectUri: str
    """
    The redirect URI for the current sign-in session.
    """
    codeVerifier: str
    """
    The code verifier of Proof Key for Code Exchange (PKCE).
    """
    state: str
    """
    The state for OAuth 2.0 authorization request.
    """


class AccessToken(BaseModel):
    """
    The access token class for a resource.
    """

    token: str
    """
    The access token string.
    """
    expiresAt: int
    """
    The timestamp (in seconds) when the access token will expire.
    Note this is not the expiration time of the access token itself, but the
    expiration time of the access token cache.
    """


class AccessTokenMap(BaseModel):
    """
    The access token map that maps the resource to the access token for that resource.

    If resource is an empty string, it means the access token is for UserInfo endpoint
    or the default resource.
    """

    x: Dict[str, AccessToken]


InteractionMode = Literal["signIn", "signUp"]
"""
The interaction mode for the sign-in request. Note this is not a part of the OIDC
specification, but a Logto extension.
"""


class LogtoClient:
    """
    The main class of the Logto client. You should create an instance of this class
    and use it to sign in, sign out, get access token, etc.
    """

    def __init__(self, config: LogtoConfig, storage: Storage = MemoryStorage()) -> None:
        self.config = config
        self._oidcCore: Optional[OidcCore] = None
        self._storage = storage

    async def getOidcCore(self) -> OidcCore:
        """
        Get the OIDC core object. You can use it to get the provider metadata, verify
        the ID token, fetch tokens by code or refresh token, etc.
        """
        if self._oidcCore is None:
            self._oidcCore = OidcCore(
                await OidcCore.getProviderMetadata(
                    f"{self.config.endpoint}/oidc/.well-known/openid-configuration"
                )
            )
        return self._oidcCore

    def _getAccessTokenMap(self) -> AccessTokenMap:
        """
        Get the access token map from storage.
        """
        accessTokenMap = self._storage.get("accessTokenMap")
        try:
            return AccessTokenMap.model_validate_json(accessTokenMap)
        except:
            return AccessTokenMap(x={})

    def _setAccessToken(self, resource: str, accessToken: str, expiresIn: int) -> None:
        """
        Set the access token for the given resource to storage.
        """
        accessTokenMap = self._getAccessTokenMap()
        accessTokenMap.x[resource] = AccessToken(
            token=accessToken,
            expiresAt=int(time.time())
            + expiresIn
            - 60,  # 60 seconds earlier to avoid clock skew
        )
        self._storage.set("accessTokenMap", accessTokenMap.model_dump_json())

    def _getAccessToken(self, resource: str) -> Optional[str]:
        """
        Get the valid access token for the given resource from storage, no refresh will be
        performed.
        """
        accessTokenMap = self._getAccessTokenMap()
        accessToken = accessTokenMap.x.get(resource, None)
        if accessToken is None or accessToken.expiresAt < int(time.time()):
            return None
        return accessToken.token

    async def _handleTokenResponse(
        self, resource: str, tokenResponse: TokenResponse
    ) -> None:
        """
        Handle the token response from the Logto server and store the tokens to storage.

        Resource can be an empty string, which means the access token is for UserInfo
        endpoint or the default resource.
        """
        if tokenResponse.id_token is not None:
            (await self.getOidcCore()).verifyIdToken(
                tokenResponse.id_token, self.config.appId
            )
            self._storage.set("idToken", tokenResponse.id_token)

        if tokenResponse.refresh_token is not None:
            self._storage.set("refreshToken", tokenResponse.refresh_token)

        self._setAccessToken(
            resource, tokenResponse.access_token, tokenResponse.expires_in
        )

    async def _buildSignInUrl(
        self,
        redirectUri: str,
        codeChallenge: str,
        state: str,
        interactionMode: Optional[InteractionMode] = None,
    ) -> str:
        appId, prompt, resources, scopes = (
            self.config.appId,
            self.config.prompt,
            self.config.resources,
            self.config.scopes,
        )
        authorizationEndpoint = (
            await self.getOidcCore()
        ).metadata.authorization_endpoint
        query = urllib.parse.urlencode(
            removeFalsyKeys(
                {
                    "client_id": appId,
                    "redirect_uri": redirectUri,
                    "response_type": "code",
                    "scope": " ".join(
                        (item.value if isinstance(item, Scope) else item)
                        for item in (scopes + OidcCore.defaultScopes)
                    ),
                    "resource": (
                        list(set(resources + [ReservedResource.organizations.value]))
                        if UserInfoScope.organizations in scopes
                        else resources
                    ),
                    "prompt": prompt,
                    "code_challenge": codeChallenge,
                    "code_challenge_method": "S256",
                    "state": state,
                    "interaction_mode": interactionMode,
                }
            ),
            True,
        )
        return f"{authorizationEndpoint}?{query}"

    def _getSignInSession(self) -> Optional[SignInSession]:
        """
        Try to parse the current sign-in session from storage. If the value does not
        exist or parse failed, return None.
        """
        signInSession = self._storage.get("signInSession")
        if signInSession is None:
            return None
        try:
            return SignInSession.model_validate_json(signInSession)
        except:
            return None

    def _setSignInSession(self, signInSession: SignInSession) -> None:
        self._storage.set("signInSession", signInSession.model_dump_json())

    async def signIn(
        self, redirectUri: str, interactionMode: Optional[InteractionMode] = None
    ) -> str:
        """
        Returns the sign-in URL for the given redirect URI. You should redirect the user
        to the returned URL to sign in.

        By specifying the interaction mode, you can control whether the user will be
        prompted for sign-in or sign-up on the first screen. If the interaction mode is
        not specified, the default one will be used.

        Example:
          ```python
          return redirect(await client.signIn('https://example.com/callback'))
          ```
        """
        codeVerifier = OidcCore.generateCodeVerifier()
        codeChallenge = OidcCore.generateCodeChallenge(codeVerifier)
        state = OidcCore.generateState()
        signInUrl = await self._buildSignInUrl(
            redirectUri, codeChallenge, state, interactionMode
        )

        self._setSignInSession(
            SignInSession(
                redirectUri=redirectUri,
                codeVerifier=codeVerifier,
                state=state,
            )
        )
        for key in ["idToken", "accessToken", "refreshToken"]:
            self._storage.delete(key)

        return signInUrl

    async def signOut(self, postLogoutRedirectUri: Optional[str] = None) -> str:
        """
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
        """
        self._storage.delete("idToken")
        self._storage.delete("refreshToken")
        self._storage.delete("accessTokenMap")

        endSessionEndpoint = (await self.getOidcCore()).metadata.end_session_endpoint

        if endSessionEndpoint is None:
            raise LogtoException(
                "End session endpoint not found in the provider metadata"
            )

        return (
            endSessionEndpoint
            + "?"
            + urllib.parse.urlencode(
                removeFalsyKeys(
                    {
                        "client_id": self.config.appId,
                        "post_logout_redirect_uri": postLogoutRedirectUri,
                    }
                )
            )
        )

    async def handleSignInCallback(self, callbackUri: str) -> None:
        """
        Handle the sign-in callback from the Logto server. This method should be called
        in the callback route handler of your application.
        """
        signInSession = self._getSignInSession()

        if signInSession is None:
            raise LogtoException("Sign-in session not found")

        # Validate the callback URI without query matches the redirect URI
        parsedCallbackUri = urllib.parse.urlparse(callbackUri)

        if (
            parsedCallbackUri.path
            != urllib.parse.urlparse(signInSession.redirectUri).path
        ):
            raise LogtoException(
                "The URI path does not match the redirect URI in the sign-in session"
            )

        query = urllib.parse.parse_qs(parsedCallbackUri.query)

        if "error" in query:
            raise LogtoException(query["error"][0])

        if signInSession.state != query.get("state", [None])[0]:
            raise LogtoException("Invalid state in the callback URI")

        code = query.get("code", [None])[0]
        if code is None:
            raise LogtoException("Code not found in the callback URI")

        tokenResponse = await (await self.getOidcCore()).fetchTokenByCode(
            clientId=self.config.appId,
            clientSecret=self.config.appSecret,
            redirectUri=signInSession.redirectUri,
            code=code,
            codeVerifier=signInSession.codeVerifier,
        )

        await self._handleTokenResponse("", tokenResponse)
        self._storage.delete("signInSession")

    async def getAccessToken(self, resource: str = "") -> Optional[str]:
        """
        Get the access token for the given resource. If the access token is expired,
        it will be refreshed automatically. If no refresh token is found, None will
        be returned.
        """
        accessToken = self._getAccessToken(resource)
        if accessToken is not None:
            return accessToken

        if (
            resource.startswith(OrganizationUrnPrefix)
            and UserInfoScope.organizations not in self.config.scopes
        ):
            raise LogtoException(
                "The `UserInfoScope.organizations` scope is required to fetch organization tokens"
            )

        refreshToken = self._storage.get("refreshToken")
        if refreshToken is None:
            return None

        tokenResponse = await (await self.getOidcCore()).fetchTokenByRefreshToken(
            clientId=self.config.appId,
            clientSecret=self.config.appSecret,
            refreshToken=refreshToken,
            resource=resource,
        )

        await self._handleTokenResponse(resource, tokenResponse)
        return tokenResponse.access_token

    async def getOrganizationToken(self, organizationId: str) -> Optional[str]:
        """
        Get the access token for the given organization ID. If the access token is expired,
        it will be refreshed automatically. If no refresh token is found, None will
        be returned.
        """
        return await self.getAccessToken(buildOrganizationUrn(organizationId))

    async def getAccessTokenClaims(self, resource: str = "") -> AccessTokenClaims:
        """
        Get the claims in the access token for the given resource. If the access token
        is expired, it will be refreshed automatically. If it's unable to refresh the
        access token, an exception will be thrown.
        """
        accessToken = await self.getAccessToken(resource)
        return OidcCore.decodeAccessToken(accessToken)

    async def getOrganizationTokenClaims(
        self, organizationId: str
    ) -> AccessTokenClaims:
        """
        Get the claims in the access token for the given organization ID. If the access token
        is expired, it will be refreshed automatically. If it's unable to refresh the
        access token, an exception will be thrown.
        """
        return await self.getAccessTokenClaims(buildOrganizationUrn(organizationId))

    def getIdToken(self) -> Optional[str]:
        """
        Get the ID Token string. If you need to get the claims in the ID Token, use
        `getIdTokenClaims` instead.
        """
        return self._storage.get("idToken")

    def getIdTokenClaims(self) -> IdTokenClaims:
        """
        Get the claims in the ID Token. If the ID Token does not exist, an exception
        will be thrown.
        """
        idToken = self._storage.get("idToken")
        if idToken is None:
            raise LogtoException("ID Token not found")

        return OidcCore.decodeIdToken(idToken)

    def getRefreshToken(self) -> Optional[str]:
        """
        Get the refresh token string.
        """
        return self._storage.get("refreshToken")

    def isAuthenticated(self) -> bool:
        """
        Check if the user is authenticated by checking if the ID Token exists.
        """
        return self._storage.get("idToken") is not None

    async def fetchUserInfo(self) -> UserInfoResponse:
        """
        Fetch the user information from the UserInfo endpoint. If the access token
        is expired, it will be refreshed automatically.
        """
        accessToken = await self.getAccessToken()
        return await (await self.getOidcCore()).fetchUserInfo(accessToken)
