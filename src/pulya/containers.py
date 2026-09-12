from contextvars import ContextVar
from typing import TypeVar

import msgspec
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Dependency,
    Factory,
    Provider,
)

from pulya.headers import Headers
from pulya.request import Request

T = TypeVar("T")


class _BodyWrapper:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def deserialize(self, body_arg_schema: type[T]) -> T:
        content = self.content or b"null"
        return msgspec.json.decode(content, type=body_arg_schema)


class _BearerToken:
    """Extracts a bearer token from the Authorization header."""

    def __init__(self, headers: Headers) -> None:
        self._headers = headers

    def extract(self) -> str | None:
        authorization = self._headers.get("authorization")
        if authorization is None:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        return token


class RequestContainer(DeclarativeContainer):
    ctx = Dependency(ContextVar)
    request: Provider[Request] = Factory(ctx.provided.get.call())

    headers = Factory(request.provided.headers)
    body = Factory(_BodyWrapper, request.provided.get_content.call())
    bearer_token = Factory(_BearerToken, request.provided.headers)
