from collections import defaultdict
from collections.abc import Callable, Mapping
from http import HTTPMethod
from typing import Any, Protocol, TypeVar, get_args, get_type_hints

import msgspec
from matchit import Router as MatchitRouter

T = TypeVar("T", bound=Callable[..., Any])


class CreateRouteSignature(Protocol):
    def __call__(self, url_pattern: str) -> Callable[[T], T]:
        """Helpful method"""
        ...


class Route:
    __slots__ = [
        "body_arg_name",
        "body_arg_schema",
        "handler",
        "handler_type_hint",
        "method",
        "path_params_schema",
        "url_pattern",
    ]

    def __init__(
        self, method: HTTPMethod, url_pattern: str, handler: Callable[..., Any]
    ) -> None:
        self.method = method
        self.handler = handler
        self.url_pattern = url_pattern

        self.handler_type_hint = get_type_hints(handler, include_extras=True)

        fields = set(self.handler_type_hint.keys()) - {"return"}

        # Remove fields handled by DI
        for k, param in self.handler_type_hint.items():
            param_args = get_args(param)
            for arg in param_args:
                if getattr(arg, "__IS_MARKER__", False):
                    fields.remove(k)
                    break

        self.path_params_schema = msgspec.defstruct("PathParams", fields=fields)


class _MethodFactory:
    def __init__(self, method: HTTPMethod) -> None:
        self.method = method

    def __get__(self, instance: "Router", owner: type) -> CreateRouteSignature:
        def _method(url_pattern: str) -> Callable[[T], T]:
            def _inner(handler: T) -> T:
                instance.add_route(
                    self.method, url_pattern=url_pattern, handler=handler
                )
                return handler

            return _inner

        return _method


class Router:
    def __init__(self) -> None:
        self._routers_by_method: dict[HTTPMethod, MatchitRouter[Route]] = defaultdict(
            lambda: MatchitRouter()
        )

    get = _MethodFactory(HTTPMethod.GET)
    post = _MethodFactory(HTTPMethod.POST)
    put = _MethodFactory(HTTPMethod.PUT)
    delete = _MethodFactory(HTTPMethod.DELETE)

    def add_route(
        self, method: HTTPMethod, url_pattern: str, handler: Callable[..., Any]
    ) -> None:
        route = Route(method=method, url_pattern=url_pattern, handler=handler)
        self._routers_by_method[method].insert(url_pattern, route)

    def match_route(
        self, method: HTTPMethod, path: str
    ) -> tuple[Route, Mapping[str, str]] | None:
        try:
            res = self._routers_by_method[method].at(path)
        except LookupError:
            return None
        return res.value, res.params
