from http import HTTPMethod
from typing import Protocol

from pulya.headers import Headers


class Request(Protocol):
    __slots__ = ()

    @property
    def method(self) -> HTTPMethod: ...

    @property
    def path(self) -> str: ...

    @property
    def headers(self) -> Headers: ...

    async def get_content(self) -> bytes:
        """Read whole request body."""
