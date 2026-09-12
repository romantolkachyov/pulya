"""Tests for the Depends marker."""

from collections.abc import AsyncGenerator, Callable
from http import HTTPStatus
from typing import Annotated, Any, cast

import pytest
from dependency_injector import containers
from dependency_injector.wiring import Provide, inject

from pulya import Depends, Pulya, RequestContainer, TestClient
from pulya.headers import Headers


async def get_async_value() -> str:
    """Async dependency without markers."""
    return "async-value"


def get_sync_value() -> str:
    """Sync dependency without markers."""
    return "sync-value"


class DependsContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[__name__])


app = Pulya(DependsContainer)


@app.get("/async")
async def async_handler(value: str = Depends(get_async_value)) -> dict[str, Any]:
    return {"value": value}


@app.get("/sync")
async def sync_handler(value: str = Depends(get_sync_value)) -> dict[str, Any]:
    return {"value": value}


@app.get("/wrapped")
@inject
async def wrapped_handler(
    headers: Annotated[Headers, Provide[RequestContainer.headers]],
    value: str = Depends(get_sync_value),
) -> dict[str, Any]:
    """Explicitly @inject-wrapped handler with Depends (legacy style)."""
    return {"value": value, "headers": len(list(headers))}


@app.get("/annotated")
async def annotated_handler(
    value: Annotated[str, Depends(get_async_value)],
) -> dict[str, Any]:
    """Depends as Annotated metadata instead of a default value."""
    return {"value": value}


@app.get("/annotated-mixed")
async def annotated_mixed_handler(
    headers: Annotated[Headers, Provide[RequestContainer.headers]],
    value: Annotated[str, Depends(get_sync_value)],
) -> dict[str, Any]:
    """Annotated Depends combined with wiring markers."""
    return {"value": value, "headers": len(list(headers))}


@pytest.fixture
async def client() -> AsyncGenerator[TestClient, Any]:
    async with TestClient(app=app) as client:
        yield client


async def test_depends_async(client: TestClient) -> None:
    """Async Depends value is awaited and passed to the handler."""
    resp = await client.get("/async")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"value": "async-value"}


async def test_depends_sync(client: TestClient) -> None:
    """Sync Depends value is passed to the handler."""
    resp = await client.get("/sync")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"value": "sync-value"}


async def test_depends_on_inject_wrapped_handler(client: TestClient) -> None:
    """Depends works on handlers already wrapped with @inject."""
    resp = await client.get("/wrapped")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["value"] == "sync-value"
    assert data["headers"] > 0


async def test_depends_annotated(client: TestClient) -> None:
    """Depends works as Annotated metadata."""
    resp = await client.get("/annotated")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"value": "async-value"}


async def test_depends_annotated_with_markers(client: TestClient) -> None:
    """Annotated Depends works together with wiring markers."""
    resp = await client.get("/annotated-mixed")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["value"] == "sync-value"
    assert data["headers"] > 0


def test_depends_function_unit_testable() -> None:
    """Depends functions are plain functions: callable without wiring."""
    assert get_sync_value() == "sync-value"
    # no markers -> stored as-is, not wrapped with the wiring resolver
    marker = cast("Any", Depends(get_sync_value))
    assert marker.fn is get_sync_value


async def test_async_depends_unit_testable() -> None:
    """Async Depends functions are awaitable without wiring."""
    assert await get_async_value() == "async-value"


def test_depends_marker_in_default_value() -> None:
    """Markers provided as default values are detected and wrapped."""

    def fn(value: Any = Provide[RequestContainer.request]) -> Any:
        return value

    assert Depends(fn).fn is not fn


def test_depends_callable_without_signature() -> None:
    """Callables without a signature are stored as-is."""

    def fn(value: Any) -> Any:
        return value

    no_signature = cast("Callable[..., Any]", object())
    assert Depends(no_signature).fn is no_signature


def test_depends_unresolvable_annotation() -> None:
    """Unresolvable forward references do not break marker detection."""

    def fn(value: "NonExistentType") -> None: ...

    # Visible to mypy in this scope, but missing from the module globals
    # that get_type_hints() resolves against at runtime.
    type NonExistentType = str

    marker = cast("Any", Depends(fn))
    assert marker.fn is fn
