from abc import ABC
from asyncio import AbstractEventLoop
from collections import defaultdict
from collections.abc import AsyncIterator, Iterable, Iterator
from http import HTTPMethod, HTTPStatus
from typing import Literal, Protocol

import msgspec

from pulya.application import AbstractApplication
from pulya.headers import Headers
from pulya.request import Request
from pulya.responses import Response


class _Headers(Protocol):
    """RSGI headers interface."""

    def __getitem__(self, item: str) -> str: ...
    def __iter__(self) -> Iterator[str]: ...
    def get_all(self, key: str) -> list[str]:
        """Get all values from headers with specified name."""

    def items(self) -> Iterable[tuple[str, str]]: ...


class Scope:
    """RSGI scope interface."""

    proto: Literal["http", "ws"]
    #: a string containing the version of the RSGI spec
    rsgi_version: str
    #: a string containing the HTTP version (one of "1", "1.1" or "2")
    http_version: str
    #: a string in the format {address}:{port}, where host is the listening address
    #:  for this server, and port is the integer listening port
    server: str
    #: a string in the format {address}:{port}, where host is the remote host's address
    #:  and port is the remote port
    client: str
    #: URL scheme portion (one of "http" or "https")
    scheme: Literal["http", "https"]
    #: the HTTP method name, uppercased
    method: str
    #: HTTP request target excluding any query string
    path: str
    #: URL portion after the ?
    query_string: str
    #: a mapping-like object, where key is the header name,
    #: and value is the header value;
    #: header names are always lower-case; a get_all method returns a list of all the
    #: header values for the given key
    headers: _Headers
    #: an optional string containing the relevant pseudo-header
    #: (empty on HTTP versions prior to 2)
    authority: str | None

    def __init__(
        self,
        proto: Literal["http", "ws"],
        rsgi_version: str,
        http_version: str,
        server: str,
        client: str,
        scheme: Literal["http", "https"],
        method: str,
        path: str,
        query_string: str,
        headers: _Headers,
        authority: str | None = None,
    ) -> None:
        self.proto = proto
        self.rsgi_version = rsgi_version
        self.http_version = http_version
        self.server = server
        self.client = client
        self.scheme = scheme
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers
        self.authority = authority


class Transport(Protocol):
    """RSGI transport object interface."""

    async def send_bytes(self, content: bytes) -> None: ...
    async def send_str(self, content: str) -> None: ...


class HTTPProtocol(Protocol):
    """RSGI protocol interface definition."""

    async def __call__(self) -> bytes:
        """__call__ to receive the entire body in bytes format."""
        ...

    async def __aiter__(self) -> AsyncIterator[bytes]:
        """__aiter__ to receive the body in bytes chunks."""
        ...

    async def client_disconnect(self) -> None:
        """Client_disconnect to watch for client disconnection."""
        ...

    def response_empty(self, status: int, headers: list[tuple[str, str]]) -> None:
        """Response_empty to send back an empty response."""
        ...

    def response_str(
        self, status: int, headers: list[tuple[str, str]], body: str
    ) -> None:
        """Response_str to send back a response with a str body."""
        ...

    def response_bytes(
        self, status: int, headers: list[tuple[str, str]], body: bytes
    ) -> None:
        """Response_bytes to send back a response with bytes body."""
        ...

    def response_file(
        self, status: int, headers: list[tuple[str, str]], file: str
    ) -> None:
        """Response_file to send back a file response (from its path)."""
        ...

    def response_file_range(
        self,
        status: int,
        headers: list[tuple[str, str]],
        file: str,
        start: int,
        end: int,
    ) -> None:
        """Response_file_range to send back a file range response (from its path)."""
        ...

    def response_stream(self, status: int, headers: list[tuple[str, str]]) -> Transport:
        """Response_stream to start a stream response."""
        ...


class RSGIRequest(Request):
    """
    RSGI request adapter.

    Implements Request interface over RSGI scope and protocol.
    """

    __slots__ = ("_protocol", "_scope")

    def __init__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        self._scope = scope
        self._protocol = protocol

    @property
    def method(self) -> HTTPMethod:
        return HTTPMethod(self._scope.method)

    @property
    def path(self) -> str:
        return self._scope.path

    @property
    def headers(self) -> Headers:
        return RSGIHeaders(self._scope.headers)

    async def get_content(self) -> bytes:
        return await self._protocol()


class RSGIHeaders(Headers):
    def __init__(self, headers: _Headers | None = None) -> None:
        self._headers = defaultdict(list)
        if headers is not None:
            for k in headers:
                self.set_list(k, headers.get_all(k))


class RSGIApplication(AbstractApplication, ABC):
    """Pulya RSGI application interface implementation."""

    async def __rsgi__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        if scope.proto != "http":  # pragma: no cover
            msg = f"Unsupported protocol {scope.proto}"
            raise RuntimeError(msg)

        response = await self.handle_http_request(RSGIRequest(scope, protocol))

        if isinstance(response, Response):
            protocol.response_bytes(
                status=response.status, headers=response.headers, body=response.content
            )
        elif isinstance(response, bytes):
            protocol.response_bytes(status=HTTPStatus.OK, headers=[], body=response)
        elif isinstance(response, str):
            protocol.response_bytes(
                status=HTTPStatus.OK, headers=[], body=response.encode()
            )
        elif isinstance(response, (msgspec.Struct, dict, list, str, int)):
            protocol.response_bytes(
                status=HTTPStatus.OK, headers=[], body=msgspec.json.encode(response)
            )
        else:  # pragma: no cover
            msg = f"Unsupported response type {type(response)}"
            raise TypeError(msg)

    def __rsgi_init__(self, loop: AbstractEventLoop) -> None:
        loop.run_until_complete(self.on_startup())

    def __rsgi_del__(self, loop: AbstractEventLoop) -> None:
        loop.run_until_complete(self.on_shutdown())
