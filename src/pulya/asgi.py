from abc import ABC
from collections import defaultdict
from collections.abc import Iterable
from http import HTTPMethod, HTTPStatus

import msgspec
from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
    HTTPScope,
    LifespanShutdownCompleteEvent,
    LifespanStartupCompleteEvent,
)
from asgiref.typing import Scope as ASGIScope

from pulya.application import AbstractApplication
from pulya.headers import Headers
from pulya.request import Request
from pulya.responses import Response


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
            else:  # pragma: no cover
                msg = f"Unsupported ASGI message type {message['type']}"
                raise RuntimeError(msg)
        return body


class ASGIHeaders(Headers):
    """
    ASGI headers adapter.

    Adopts headers structure defined in ASGI scope to internal one.
    """

    def __init__(self, headers: Iterable[tuple[bytes, bytes]] | None = None) -> None:
        self._headers = defaultdict(list)
        if headers:
            for k, v in headers:
                self.add(k.decode(), v.decode())


class ASGIApplication(AbstractApplication, ABC):
    """Pulya ASGI application interface implementation."""

    async def __call__(
        self, scope: ASGIScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await self.on_startup()
                    await send(
                        LifespanStartupCompleteEvent(type="lifespan.startup.complete")
                    )
                if message["type"] == "lifespan.shutdown":
                    await self.on_shutdown()
                    await send(
                        LifespanShutdownCompleteEvent(type="lifespan.shutdown.complete")
                    )
                    return
        elif scope["type"] == "http":
            response = await self.handle_http_request(ASGIRequest(scope, receive))

            if isinstance(response, Response):
                await send(
                    HTTPResponseStartEvent(
                        type="http.response.start",
                        status=response.status,
                        headers=[
                            (b"content-type", b"text/plain"),
                        ],
                        trailers=False,
                    )
                )
                await send(
                    HTTPResponseBodyEvent(
                        type="http.response.body",
                        body=response.content,
                        more_body=False,
                    )
                )
            elif isinstance(response, str):
                await send(
                    HTTPResponseStartEvent(
                        type="http.response.start",
                        status=HTTPStatus.OK,  # TODO @roman: get default status
                        headers=[
                            (b"content-type", b"text/plain"),
                        ],
                        trailers=False,
                    )
                )
                await send(
                    HTTPResponseBodyEvent(
                        type="http.response.body",
                        body=response.encode(),
                        more_body=False,
                    )
                )
            elif isinstance(response, bytes):
                await send(
                    HTTPResponseStartEvent(
                        type="http.response.start",
                        status=HTTPStatus.OK,  # TODO @roman: get default status
                        headers=[
                            (b"content-type", b"text/plain"),
                        ],
                        trailers=False,
                    )
                )
                await send(
                    HTTPResponseBodyEvent(
                        type="http.response.body",
                        body=response,
                        more_body=False,
                    )
                )
            elif isinstance(response, (msgspec.Struct, dict, list, str, int | bytes)):
                await send(
                    HTTPResponseStartEvent(
                        type="http.response.start",
                        status=HTTPStatus.OK,  # TODO @roman: get default status
                        headers=[
                            (b"content-type", b"text/plain"),
                        ],
                        trailers=False,
                    )
                )
                await send(
                    HTTPResponseBodyEvent(
                        type="http.response.body",
                        body=msgspec.json.encode(response),
                        more_body=False,
                    )
                )
            else:  # pragma: no cover
                msg = f"Unsupported response type {type(response)}"
                raise RuntimeError(msg)
        else:  # pragma: no cover
            msg = f"Unsupported scope type {type(scope['type'])}"
            raise RuntimeError(msg)
