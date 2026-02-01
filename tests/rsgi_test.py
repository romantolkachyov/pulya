import asyncio
from collections import UserDict
from collections.abc import AsyncIterator

import msgspec.json

from examples.simple_example import app
from pulya.rsgi import Scope, Transport


class StubHTTPProtocol:
    """RSGI protocol object implementation for testing."""

    async def __call__(self) -> bytes:
        """__call__ to receive the entire body in bytes format."""
        return msgspec.json.encode({"items": []})

    async def __aiter__(self) -> AsyncIterator[bytes]:
        """__aiter__ to receive the body in bytes chunks."""
        raise NotImplementedError

    async def client_disconnect(self) -> None:
        """Client_disconnect to watch for client disconnection."""
        raise NotImplementedError

    def response_empty(self, status: int, headers: list[tuple[str, str]]) -> None:
        """Response_empty to send back an empty response."""
        raise NotImplementedError

    def response_str(
        self, status: int, headers: list[tuple[str, str]], body: str
    ) -> None:
        """Response_str to send back a response with a str body."""
        raise NotImplementedError

    def response_bytes(
        self,
        status: int,  # noqa: ARG002
        headers: list[tuple[str, str]],  # noqa: ARG002
        body: bytes,  # noqa: ARG002
    ) -> None:
        """Response_bytes to send back a response with bytes body."""
        return

    def response_file(
        self, status: int, headers: list[tuple[str, str]], file: str
    ) -> None:
        """Response_file to send back a file response (from its path)."""
        raise NotImplementedError

    def response_file_range(
        self,
        status: int,
        headers: list[tuple[str, str]],
        file: str,
        start: int,
        end: int,
    ) -> None:
        """Response_file_range to send back a file range response (from its path)."""
        raise NotImplementedError

    def response_stream(self, status: int, headers: list[tuple[str, str]]) -> Transport:
        """Response_stream to start a stream response."""
        raise NotImplementedError


class StubHeaders(UserDict[str, str]):
    def get_all(self, name: str) -> list[str]:
        return [self[name]]


def test_rsgi_application() -> None:
    event_loop = asyncio.new_event_loop()
    app.__rsgi_init__(event_loop)
    event_loop.run_until_complete(
        app.__rsgi__(
            Scope(
                proto="http",
                rsgi_version="1.0",
                http_version="2.0",
                server="server",
                client="client",
                scheme="http",
                method="GET",
                path="/headers/",
                query_string="",
                headers=StubHeaders({"X-Sample": "example Value"}),
                authority=None,
            ),
            StubHTTPProtocol(),
        )
    )
    event_loop.run_until_complete(
        app.__rsgi__(
            Scope(
                proto="http",
                rsgi_version="1.0",
                http_version="2.0",
                server="server",
                client="client",
                scheme="http",
                method="POST",
                path="/echo",
                query_string="",
                headers=StubHeaders({"X-Sample": "example Value"}),
                authority=None,
            ),
            StubHTTPProtocol(),
        )
    )
    event_loop.run_until_complete(
        app.__rsgi__(
            Scope(
                proto="http",
                rsgi_version="1.0",
                http_version="2.0",
                server="server",
                client="client",
                scheme="http",
                method="GET",
                path="/plain_response/",
                query_string="",
                headers=StubHeaders({"X-Sample": "example Value"}),
                authority=None,
            ),
            StubHTTPProtocol(),
        )
    )
    app.__rsgi_del__(event_loop)
