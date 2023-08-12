import time
from typing import Any, Callable, Dict, Optional
from jwt import PyJWK
import jwt
from pytest_mock import MockerFixture
import pytest

from . import LogtoException
from .utilities.test import mockHttp, mockProviderMetadata
from .models.response import TokenResponse, UserInfoResponse
from .models.oidc import IdTokenClaims, AccessTokenClaims, OidcProviderMetadata
from .OidcCore import OidcCore

MockRequest = Callable[..., None]


class TestOidcCoreStatic:
    def test_generateState(self):
        assert len(OidcCore.generateState()) == 43

    def test_generateCodeVerifier(self):
        assert len(OidcCore.generateCodeVerifier()) == 43

    def test_generateCodeChallenge(self):
        codeVerifier = "12345678901234567890123456789012345678901234567890"
        assert (
            OidcCore.generateCodeChallenge(codeVerifier)
            == "9Y__uhKapn7GO_ElcaQpd8C3hdOyqTzAU4VXyR2iEV0"
        )

    def test_decodeIdToken(self):
        idToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJodHRwczovL2xvZ3RvLmFwcCIsImF1ZCI6ImZvbyIsImV4cCI6MTYxNjQ0NjQwMCwiaWF0IjoxNjE2NDQ2MzAwLCJzdWIiOiJ1c2VyMSIsIm5hbWUiOiJKb2huIFdpY2siLCJ1c2VybmFtZSI6ImpvaG4iLCJlbWFpbCI6ImpvaG5Ad2ljay5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0.12345678901234567890123456789012345678901234567890"
        assert OidcCore.decodeIdToken(idToken) == IdTokenClaims(
            iss="https://logto.app",
            aud="foo",
            exp=1616446400,
            iat=1616446300,
            sub="user1",
            name="John Wick",
            username="john",
            email="john@wick.com",
            email_verified=True,
        )

    def test_decodeAccessTokenWithResourceAndClientId(self):
        accessToken = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJodHRwczovL2xvZ3RvLmFwcCIsImF1ZCI6Imh0dHBzOi8vbG9ndG8uYXBwL2FwaSIsImV4cCI6MTYxNjQ0NjQwMCwiaWF0IjoxNjE2NDQ2MzAwLCJzdWIiOiJ1c2VyMSIsInNjb3BlIjoiYWRtaW4gdXNlciIsImNsaWVudF9pZCI6InNhcXJlMW9xYmtwajZ6aHE4NWhvMCJ9.12345678901234567890123456789012345678901234567890"
        assert OidcCore.decodeAccessToken(accessToken) == AccessTokenClaims(
            iss="https://logto.app",
            aud="https://logto.app/api",
            exp=1616446400,
            iat=1616446300,
            sub="user1",
            scope="admin user",
            client_id="saqre1oqbkpj6zhq85ho0",
        )


class TestOidcCore:
    @pytest.fixture
    def oidcCore(self, metadata: OidcProviderMetadata) -> OidcCore:
        return OidcCore(metadata)

    @pytest.fixture
    def metadata(self) -> OidcProviderMetadata:
        return mockProviderMetadata

    @pytest.fixture
    def tokenResponse(self) -> TokenResponse:
        return TokenResponse(access_token="token", token_type="Bearer", expires_in=3600)

    @pytest.fixture
    def mockRequest(self, mocker: MockerFixture) -> MockRequest:
        def _mock(
            method: str = "get",
            json: Optional[Dict[str, Any]] = None,
            text: Optional[str] = None,
            status: int = 200,
        ):
            return mockHttp(mocker, method, json, text, status)

        return _mock

    async def test_getProviderMetadata(
        self,
        metadata: OidcProviderMetadata,
        mockRequest: MockRequest,
    ) -> None:
        discovery_url = "https://discovery.url"
        mockRequest(json=metadata.__dict__)
        result = await OidcCore.getProviderMetadata(discovery_url)

        assert result == metadata

    async def test_fetchTokenByCode(
        self,
        oidcCore: OidcCore,
        tokenResponse: TokenResponse,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(method="post", json=tokenResponse.__dict__)
        result = await oidcCore.fetchTokenByCode(
            "clientId", "clientSecret", "redirectUri", "code", "codeVerifier"
        )

        assert result == tokenResponse

    async def test_fetchTokenByCode_failure(
        self,
        oidcCore: OidcCore,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(method="post", text="error", status=400)
        with pytest.raises(LogtoException, match="error"):
            await oidcCore.fetchTokenByCode(
                "clientId", "clientSecret", "redirectUri", "code", "codeVerifier"
            )

    async def test_fetchTokenByRefreshToken(
        self,
        oidcCore: OidcCore,
        tokenResponse: TokenResponse,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(method="post", json=tokenResponse.__dict__)
        result = await oidcCore.fetchTokenByRefreshToken(
            "clientId", "clientSecret", "refreshToken"
        )

        assert result == tokenResponse

    async def test_fetchTokenByRefreshToken_failure(
        self,
        oidcCore: OidcCore,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(method="post", text="error", status=400)
        with pytest.raises(LogtoException, match="error"):
            await oidcCore.fetchTokenByRefreshToken(
                "clientId", "clientSecret", "refreshToken"
            )

    async def test_verifyIdToken(
        self,
        oidcCore: OidcCore,
        mocker: MockerFixture,
    ) -> None:
        # Mock PyJWK with a valid key
        jwk = PyJWK(
            jwk_data={
                "kty": "EC",
                "d": "EQw2P8sukYhYuc_H8Q5pV8oTlXfAd7TM1mB4fwrYuw4BGFBcFx-Y9q5g6lvyxfG9",
                "use": "sig",
                "crv": "P-384",
                "kid": "1",
                "x": "GWEhvHiHu2nfZNn741QeWPyn3Laphn11wcD9c5LWqPQTaqw-SlJIWXavrvl4Yv7f",
                "y": "0KiYwX8U2pb74HCRby6ljlNgQGD-v_j5QN-MzXObRYa7XRQzKCrqj0_4BZN6UcS6",
                "alg": "ES384",
            }
        )

        idToken = IdTokenClaims(
            iss="https://logto.app",
            aud="foo",
            exp=int(time.time() - 10),  # Test for the leeway
            iat=1616446300,
            sub="user1",
            name="John Wick",
            username="john",
            email="john@wick.com",
            email_verified=True,
        )

        # Sign the idToken with the private key
        idTokenString = jwt.encode(
            idToken.model_dump(),
            jwk.key,
            algorithm="ES384",
            headers={"kid": "1"},
        )

        # Mock `get_signing_key_from_jwt` response from jwksClient
        mocker.patch(
            "jwt.jwks_client.PyJWKClient.get_signing_key_from_jwt",
            return_value=jwk,
        )

        # No error should be raised
        oidcCore.verifyIdToken(
            idToken=idTokenString,
            clientId="foo",
        )

    async def test_fetchUserInfo(
        self,
        oidcCore: OidcCore,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(json={"sub": "user1"})
        result = await oidcCore.fetchUserInfo("token")

        assert result == UserInfoResponse(sub="user1")

    async def test_fetchUserInfo_failure(
        self,
        oidcCore: OidcCore,
        mockRequest: MockRequest,
    ) -> None:
        mockRequest(text="error", status=400)
        with pytest.raises(LogtoException, match="error"):
            await oidcCore.fetchUserInfo("token")
