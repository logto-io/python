from typing import Any, Dict, Optional
from pytest_mock import MockerFixture

from logto.Storage import Storage
from logto.models.oidc import OidcProviderMetadata


class MockResponse:
    def __init__(
        self, json: Optional[Dict[str, Any]], text: Optional[str], status: int
    ) -> None:
        self._json = json
        self._text = text or str(json)
        self.status = status

    async def json(self):
        return self._json

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


def mockHttp(
    mocker: MockerFixture,
    method: str,
    json: Optional[Dict[str, Any]],
    text: Optional[str],
    status=200,
):
    mocker.patch(
        f"aiohttp.ClientSession.{method}",
        return_value=MockResponse(json=json, text=text, status=status),
    )


mockProviderMetadata = OidcProviderMetadata(
    issuer="https://logto.app",
    authorization_endpoint="https://logto.app/oidc/auth",
    token_endpoint="https://logto.app/oidc/auth/token",
    userinfo_endpoint="https://logto.app/oidc/userinfo",
    jwks_uri="https://logto.app/oidc/jwks",
    response_types_supported=[],
    subject_types_supported=[],
    id_token_signing_alg_values_supported=[],
)


class MockStorage(Storage):
    def __init__(self) -> None:
        self._data: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key, None)

    def set(self, key: str, value: Optional[str]) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)
