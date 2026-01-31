from collections import defaultdict
from collections.abc import Iterable
from http import HTTPMethod

from asgiref.typing import ASGIReceiveCallable, HTTPScope

from pulya.headers import Headers
from pulya.request import Request


class ASGIRequest(Request):
    """
    ASGI request adapter.

    Implements Request interface for ASGI scope that can be handled by the application.
    """

    __slots__ = ("_receive", "_scope")

    def __init__(self, scope: HTTPScope, receive: ASGIReceiveCallable) -> None:
        self._scope = scope
        self._receive = receive

    @property
    def method(self) -> HTTPMethod:
        """HTTP method."""
        return HTTPMethod(self._scope["method"])

    @property
    def path(self) -> str:
        """Request path."""
        return self._scope["path"]

    @property
    def headers(self) -> Headers:
        """HTTP headers."""
        return ASGIHeaders(self._scope["headers"])

    async def get_content(self) -> bytes:
        """Read and return the whole request body."""
        body = b""
        more_body = True
        while more_body:
            message = await self._receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
            else:
                msg = f"Unsupported ASGI message type {message['type']}"
                raise RuntimeError(msg)
        return body


class ASGIHeaders(Headers):
    """
    ASGI headers adapter.

    Adopts headers structure defined in ASGI scope to internal one.
    """

    def __init__(self, headers: Iterable[tuple[bytes, bytes]]) -> None:
        self._headers = defaultdict(list)
        for k, v in headers:
            self.add(k.decode(), v.decode())
