"""
The core OIDC functions for the Logto client. Provider-agonistic functions
are implemented as static methods, while other functions are implemented as
instance methods.
"""

import hashlib
import secrets
import aiohttp
from jwt import PyJWKClient
import jwt
from typing import List, Optional

from .LogtoException import LogtoException
from .models.oidc import (
    AccessTokenClaims,
    IdTokenClaims,
    OAuthScope,
    OidcProviderMetadata,
    Scope,
    UserInfoScope,
)
from .models.response import TokenResponse, UserInfoResponse
from .utilities import OrganizationUrnPrefix, removeFalsyKeys, urlsafeEncode


class OidcCore:
    defaultScopes: List[Scope] = [
        UserInfoScope.openid,
        OAuthScope.offlineAccess,
        UserInfoScope.profile,
    ]

    def __init__(self, metadata: OidcProviderMetadata) -> None:
        """
        Initialize the OIDC core with the provider metadata. You can use the
        `getProviderMetadata` method to fetch the provider metadata from the
        discovery URL.
        """
        self.metadata = metadata
        self.jwksClient = PyJWKClient(
            metadata.jwks_uri, headers={"user-agent": "@logto/python", "accept": "*/*"}
        )

    def generateState() -> str:
        """
        Generate a random string (32 bytes) for the state parameter.
        """
        return urlsafeEncode(secrets.token_bytes(32))

    def generateCodeVerifier() -> str:
        """
        Generate a random code verifier string (32 bytes) for PKCE.

        See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.1
        """
        return urlsafeEncode(secrets.token_bytes(32))

    def generateCodeChallenge(codeVerifier: str) -> str:
        """
        Generate a code challenge string for the given code verifier string.

        See: https://www.rfc-editor.org/rfc/rfc7636.html#section-4.2
        """
        return urlsafeEncode(hashlib.sha256(codeVerifier.encode("ascii")).digest())

    def decodeIdToken(idToken: str) -> IdTokenClaims:
        """
        Decode the ID Token and return the claims without verifying the signature.
        """
        return IdTokenClaims(**jwt.decode(idToken, options={"verify_signature": False}))

    def decodeAccessToken(accessToken: str) -> AccessTokenClaims:
        """
        Decode the access token and return the claims without verifying the signature.
        """
        return AccessTokenClaims(
            **jwt.decode(accessToken, options={"verify_signature": False})
        )

    async def getProviderMetadata(discoveryUrl: str) -> OidcProviderMetadata:
        """
        Fetch the provider metadata from the discovery URL.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(discoveryUrl) as resp:
                json = await resp.json()
                return OidcProviderMetadata(**json)

    async def fetchTokenByCode(
        self,
        clientId: str,
        clientSecret: Optional[str],
        redirectUri: str,
        code: str,
        codeVerifier: str,
    ) -> TokenResponse:
        """
        Fetch the token from the token endpoint using the authorization code.
        """
        tokenEndpoint = self.metadata.token_endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                tokenEndpoint,
                data={
                    "grant_type": "authorization_code",
                    "client_id": clientId,
                    "client_secret": clientSecret,
                    "redirect_uri": redirectUri,
                    "code": code,
                    "code_verifier": codeVerifier,
                },
            ) as resp:
                if resp.status != 200:
                    raise LogtoException(await resp.text())

                json = await resp.json()
                return TokenResponse(**json)

    async def fetchTokenByRefreshToken(
        self,
        clientId: str,
        clientSecret: Optional[str],
        refreshToken: str,
        resource: str = "",
    ) -> TokenResponse:
        """
        Fetch the token from the token endpoint using the refresh token.

        If the resource is an organization URN, the organization ID will be extracted
        and used as the `organization_id` parameter.
        """
        tokenEndpoint = self.metadata.token_endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                tokenEndpoint,
                data=removeFalsyKeys(
                    {
                        "grant_type": "refresh_token",
                        "client_id": clientId,
                        "client_secret": clientSecret,
                        "refresh_token": refreshToken,
                        "resource": (
                            resource
                            if not resource.startswith(OrganizationUrnPrefix)
                            else None
                        ),
                        "organization_id": (
                            resource[len(OrganizationUrnPrefix) :]
                            if resource.startswith(OrganizationUrnPrefix)
                            else None
                        ),
                    }
                ),
            ) as resp:
                if resp.status != 200:
                    raise LogtoException(await resp.text())

                json = await resp.json()
                return TokenResponse(**json)

    def verifyIdToken(self, idToken: str, clientId: str) -> None:
        """
        Verify the ID Token signature and its issuer and client ID, throw an exception
        if the verification fails.
        """
        issuer = self.metadata.issuer
        signing_key = self.jwksClient.get_signing_key_from_jwt(idToken)
        jwt.decode(
            idToken,
            signing_key.key,
            algorithms=["RS256", "PS256", "ES256", "ES384", "ES512"],
            audience=clientId,
            issuer=issuer,
            leeway=30,
        )

    async def fetchUserInfo(self, accessToken: str) -> UserInfoResponse:
        """
        Fetch the user info from the OpenID Connect UserInfo endpoint.

        See: https://openid.net/specs/openid-connect-core-1_0.html#UserInfo
        """
        userInfoEndpoint = self.metadata.userinfo_endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(
                userInfoEndpoint, headers={"Authorization": f"Bearer {accessToken}"}
            ) as resp:
                if resp.status != 200:
                    raise LogtoException(await resp.text())

                json = await resp.json()
                return UserInfoResponse(**json)
