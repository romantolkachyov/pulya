from typing import Any

from dependency_injector.wiring import Provide
from mypy.types import UnionType

from pulya.containers import RequestContainer


def Body(_type: type | UnionType) -> Any:
    return Provide[RequestContainer.body.provided.deserialize.call(_type)]


def Header(name: str, default: None = None) -> Any:
    return Provide[RequestContainer.headers.provided.get.call(name, default)]
