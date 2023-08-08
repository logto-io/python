from typing import Any, Dict

from pytest_mock import MockerFixture


class MockResponse:
    def __init__(
        self, json: Dict[str, Any] | None, text: str | None, status: int
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
    json: Dict[str, Any] | None,
    text: str | None,
    status=200,
):
    mocker.patch(
        f"aiohttp.ClientSession.{method}",
        return_value=MockResponse(json=json, text=text, status=status),
    )
