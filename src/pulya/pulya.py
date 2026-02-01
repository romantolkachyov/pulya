import threading
from _contextvars import ContextVar
from http import HTTPStatus
from typing import Any

import msgspec
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.wiring import clear_cache

from pulya import RequestContainer
from pulya.asgi import ASGIApplication
from pulya.request import Request
from pulya.responses import Response
from pulya.routing import Router
from pulya.rsgi import RSGIApplication

active_request: ContextVar[Request] = ContextVar("active_request")


class Pulya[T: DeclarativeContainer](Router, RSGIApplication, ASGIApplication):
    """
    Pylya application.

    Base class for web-application implementing ASGI and RSGI interfaces.
    """

    container: T | None = None

    def __init__(self, container_class: type[T]) -> None:
        super().__init__()
        self.container_class = container_class
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
        # dependency-inject is unstable in free-threading mode
        # so creating container sequentially
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
