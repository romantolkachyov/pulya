from contextvars import ContextVar
from typing import TypeVar

import msgspec
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Dependency,
    Factory,
    Provider,
)

from pulya.request import Request

T = TypeVar("T")


class _BodyWrapper:
    def __init__(self, content: bytes):
        self.content = content

    def deserialize(self, body_arg_schema: type[T]) -> T:
        content = self.content or "null".encode()
        return msgspec.json.decode(content, type=body_arg_schema)


class RequestContainer(DeclarativeContainer):
    ctx = Dependency(ContextVar)
    request: Provider[Request] = Factory(ctx.provided.get.call())

    headers = Factory(request.provided.headers)
    body = Factory(_BodyWrapper, request.provided.get_content.call())
