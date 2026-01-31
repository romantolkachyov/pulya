from types import UnionType
from typing import Any

from dependency_injector.wiring import Provide

from pulya.containers import RequestContainer


def Body(_type: type | UnionType) -> Any:  # noqa: N802
    return Provide[RequestContainer.body.provided.deserialize.call(_type)]


def Header(name: str, default: None = None) -> Any:  # noqa: N802
    return Provide[RequestContainer.headers.provided.get.call(name, default)]
