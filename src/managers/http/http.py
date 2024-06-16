from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from aiohttp import ClientSession


class Method(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"


@dataclass
class HTTPManagerResponse:  # Модель ответа
    status_code: int
    json: dict[str, Any] | list[dict[str, Any]]


class HTTPManager:
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_X_WWW_FORM_URLENCODED: Final[str] = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA: Final[str] = "multipart/form-data"
    AUTHORIZATION: Final[str] = "Authorization"
    TEXT_HTML: Final[str] = "text/html"  # Хеадеры

    @staticmethod
    async def request(*, method: Method, url: str, headers: dict[str, str], **kwargs) -> HTTPManagerResponse:
        async with ClientSession(headers=headers) as session:
            async with session.request(method=method.value, url=url, headers=headers, **kwargs) as response:
                return HTTPManagerResponse(
                    response.status,
                    await response.json()
                )

    async def get(self, url: str, headers: dict[str, str] = None) -> HTTPManagerResponse:
        if headers is None:
            headers = {}

        return await self.request(method=Method.GET, url=url, headers=headers)

    async def post(self, url: str, headers: dict[str, str] = None, data: dict[str, str] = None) -> HTTPManagerResponse:
        if headers is None:
            headers = {}

        if data is None:
            data = {}

        return await self.request(method=Method.POST, url=url, headers=headers, data=data)
