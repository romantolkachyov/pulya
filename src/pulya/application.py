import abc
from typing import Any

from pulya.request import Request


class AbstractApplication(abc.ABC):
    @abc.abstractmethod
    async def handle_http_request(self, request: Request) -> Any: ...
    @abc.abstractmethod
    async def on_startup(self) -> None: ...
    @abc.abstractmethod
    async def on_shutdown(self) -> None: ...
