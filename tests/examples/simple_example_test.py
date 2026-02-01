import asyncio
from collections.abc import AsyncGenerator, Awaitable
from http import HTTPStatus
from typing import Any

import pytest
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGIReceiveEvent,
    ASGISendCallable,
    ASGISendEvent,
    ASGIVersions,
    LifespanScope,
    LifespanShutdownEvent,
    LifespanStartupEvent,
)

from examples.simple_example import app as simple_app
from pulya import Pulya, TestClient


async def _startup_event_receive() -> LifespanStartupEvent:
    return {"type": "lifespan.startup"}


async def _shutdown_event_receive() -> LifespanShutdownEvent:
    return {"type": "lifespan.shutdown"}


async def _fake_send(event: Any) -> None:
    pass


def _create_lifespan_receive(
    input_queue: asyncio.Queue[ASGIReceiveEvent],
) -> ASGIReceiveCallable:
    def _receive() -> Awaitable[ASGIReceiveEvent]:
        return input_queue.get()

    return _receive


def _create_lifespan_send(
    output_queue: asyncio.Queue[ASGISendEvent],
) -> ASGISendCallable:
    def _send(event: ASGISendEvent) -> Awaitable[None]:
        return output_queue.put(event)

    return _send


@pytest.fixture
def app() -> Pulya[Any]:
    return simple_app


async def _lifespan_task(
    app: ASGI3Application,
    input_queue: asyncio.Queue[ASGIReceiveEvent],
    output_queue: asyncio.Queue[ASGISendEvent],
) -> None:
    lifespan_scope = LifespanScope(
        type="lifespan",
        asgi=ASGIVersions(spec_version="3.0", version="3.0"),
    )
    await app(
        lifespan_scope,
        _create_lifespan_receive(input_queue),
        _create_lifespan_send(output_queue),
    )


@pytest.fixture
async def client(app: ASGI3Application) -> AsyncGenerator[TestClient, Any]:
    async with TestClient(app=app) as client:
        input_queue: asyncio.Queue[ASGIReceiveEvent] = asyncio.Queue()
        output_queue: asyncio.Queue[ASGISendEvent] = asyncio.Queue()
        lifespan_task = asyncio.get_running_loop().create_task(
            _lifespan_task(app, input_queue, output_queue)
        )
        await input_queue.put(LifespanStartupEvent(type="lifespan.startup"))
        await output_queue.get()
        yield client
        await input_queue.put(LifespanShutdownEvent(type="lifespan.shutdown"))
        await output_queue.get()
        await lifespan_task


async def test_unknown_route(client: TestClient) -> None:
    resp = await client.get("/unknown")
    assert resp.status_code == HTTPStatus.NOT_FOUND


async def test_simple(client: TestClient) -> None:
    resp = await client.get("/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"success": True}


async def test_two_containers_wired(client: TestClient) -> None:
    expected_name = "example"

    resp = await client.get(f"/wiring/{expected_name}")
    assert resp.status_code == HTTPStatus.OK

    data = resp.json()
    assert list(data.keys()) == ["test", "user", "name", "headers"]
    assert data["test"] == "ok"
    assert data["user"] == f"<User /wiring/{expected_name}>"
    assert data["name"] == expected_name
    assert [k for k, v in data["headers"]] == [
        "host",
        "accept",
        "accept-encoding",
        "connection",
        "user-agent",
    ]


async def test_echo(client: TestClient) -> None:
    resp = await client.post("/echo", json={"items": []})
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"items": []}
