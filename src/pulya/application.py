import threading
from asyncio import AbstractEventLoop
from contextvars import ContextVar
from http import HTTPStatus
from typing import Any, Generic, TypeVar

import msgspec
from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
    LifespanShutdownCompleteEvent,
    LifespanStartupCompleteEvent,
)
from asgiref.typing import (
    Scope as ASGIScope,
)
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.wiring import clear_cache

from pulya.asgi import ASGIRequest
from pulya.containers import RequestContainer
from pulya.request import Request
from pulya.responses import Response
from pulya.routing import Router
from pulya.rsgi import HTTPProtocol, RSGIRequest, Scope

DIContainer = TypeVar("DIContainer", bound=DeclarativeContainer)

active_request: ContextVar[Request] = ContextVar("active_request")


class Application(Router, Generic[DIContainer]):
    def __init__(self, container_class: type[DIContainer]) -> None:
        super().__init__()
        self.container_class = container_class
        self.container: DeclarativeContainer | None = None
        self._di_lock = threading.Lock()

    async def handle_http_request(self, request: Request) -> Any:
        match = self.match_route(request.method, request.path)

        if match is None:
            return Response(
                status=HTTPStatus.NOT_FOUND,
                headers=[],
                content=msgspec.json.encode({"error": "Not found."}),
            )
        route, match_dict = match
        validated_path_params = msgspec.convert(
            match_dict, type=route.path_params_schema, strict=False
        )

        handler_params = msgspec.structs.asdict(validated_path_params)
        token = active_request.set(request)
        try:
            return await route.handler(**handler_params)
        finally:
            active_request.reset(token)

    async def on_startup(self) -> None:
        # dependency-inject is unstable in free-threading mode so creating container sequentially
        with self._di_lock:
            request_container = RequestContainer(ctx=active_request)
            self.container = self.container_class(request=request_container)
            self.container.check_dependencies()
            if fut := self.container.init_resources():
                await fut
            request_container.wiring_config = self.container.wiring_config
            # DI package has incomplete typings. Will be fixed in the upcoming release.
            self.container.wire(keep_cache=True)  # type: ignore[call-arg]
            request_container.wire(keep_cache=True)  # type: ignore[call-arg]
            clear_cache()

    async def on_shutdown(self) -> None:
        with self._di_lock:
            if self.container and (fut := self.container.shutdown_resources()):
                await fut


class ASGIApplication(Application[DIContainer]):
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
                    return
                elif message["type"] == "lifespan.shutdown":
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
            elif isinstance(response, msgspec.Struct) or isinstance(
                response, (dict, list, str, int)
            ):
                await send(
                    HTTPResponseStartEvent(
                        type="http.response.start",
                        status=HTTPStatus.OK,  # FIXME: get default status
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
            else:
                raise RuntimeError(f"Unsupported response type {type(response)}")
        else:
            raise RuntimeError(f"Unsupported scope type {type(scope['type'])}")


class RSGIApplication(Application[DIContainer]):
    """Pulya RSGI application interface implementation."""

    async def __rsgi__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        assert scope.proto == "http", "WS is not supported yet"

        response = await self.handle_http_request(RSGIRequest(scope, protocol))

        if isinstance(response, Response):
            protocol.response_bytes(
                status=response.status, headers=response.headers, body=response.content
            )
        elif isinstance(response, msgspec.Struct) or isinstance(
            response, (dict, list, str, int)
        ):
            protocol.response_bytes(
                status=HTTPStatus.OK, headers=[], body=msgspec.json.encode(response)
            )
        else:
            raise RuntimeError(f"Unsupported response type {type(response)}")

    def __rsgi_init__(self, loop: AbstractEventLoop) -> None:
        # dependency-inject is unstable in free-threading mode so creating container sequentially
        loop.run_until_complete(self.on_startup())

    def __rsgi_del__(self, loop: AbstractEventLoop) -> None:
        loop.run_until_complete(self.on_shutdown())


class Pulya(RSGIApplication[DIContainer], ASGIApplication[DIContainer]):
    """Pylya application.

    Base class for web-application implementing ASGI and RSGI interfaces.
    """

    pass
