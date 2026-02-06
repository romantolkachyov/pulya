import threading
from _contextvars import ContextVar
from http import HTTPStatus
from typing import Any, ClassVar

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

    # Pre-encoded common HTTP error responses
    PRE_ENCODED_ERRORS: ClassVar[
        dict[HTTPStatus, tuple[bytes, list[tuple[str, str]]]]
    ] = {
        HTTPStatus.NOT_FOUND: (
            msgspec.json.encode({"error": "Not found."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.BAD_REQUEST: (
            msgspec.json.encode({"error": "Bad request."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.UNAUTHORIZED: (
            msgspec.json.encode({"error": "Unauthorized."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.FORBIDDEN: (
            msgspec.json.encode({"error": "Forbidden."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.METHOD_NOT_ALLOWED: (
            msgspec.json.encode({"error": "Method not allowed."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.UNPROCESSABLE_ENTITY: (
            msgspec.json.encode({"error": "Unprocessable entity."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.TOO_MANY_REQUESTS: (
            msgspec.json.encode({"error": "Too many requests."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.INTERNAL_SERVER_ERROR: (
            msgspec.json.encode({"error": "Internal server error."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.BAD_GATEWAY: (
            msgspec.json.encode({"error": "Bad gateway."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.SERVICE_UNAVAILABLE: (
            msgspec.json.encode({"error": "Service unavailable."}),
            [("Content-Type", "application/json")],
        ),
    }

    def get_pre_encoded_error_response(self, status: HTTPStatus) -> Response | None:
        """Get a pre-encoded error response if available for the given status."""
        if status in self.PRE_ENCODED_ERRORS:
            content, headers = self.PRE_ENCODED_ERRORS[status]
            return Response(content=content, status=status, headers=headers)
        return None

    def __init__(self, container_class: type[T]) -> None:
        super().__init__()
        self.container_class = container_class
        self._di_lock = threading.Lock()

    async def handle_http_request(self, request: Request) -> Any:
        if (
            request is None
            or not hasattr(request, "method")
            or not hasattr(request, "path")
        ):
            return None

        match = self.match_route(request.method, request.path)

        if match is None:
            # Use pre-encoded 404 response if available
            pre_encoded = self.get_pre_encoded_error_response(HTTPStatus.NOT_FOUND)
            if pre_encoded:
                return pre_encoded
            # If no pre-encoded response, create a new one
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
        # dependency-injector is unstable in free-threading mode
        # so creating container sequentially
        with self._di_lock:
            request_container = RequestContainer(ctx=active_request)
            self.container = self.container_class(request=request_container)
            self.container.check_dependencies()
            if fut := self.container.init_resources():
                await fut  # pragma: no cover
            request_container.wiring_config = self.container.wiring_config
            # DI package has incomplete typings. Will be fixed in the upcoming release.
            self.container.wire(keep_cache=True)  # type: ignore[call-arg]
            request_container.wire(keep_cache=True)  # type: ignore[call-arg]
            clear_cache()

    async def on_shutdown(self) -> None:
        with self._di_lock:
            if self.container and (fut := self.container.shutdown_resources()):
                await fut  # pragma: no cover
