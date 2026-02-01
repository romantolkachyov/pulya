from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Any

import pytest
from asgiref.typing import (
    ASGI3Application,
)

from examples.simple_example import app as simple_app
from pulya import TestClient


@pytest.fixture
def app() -> ASGI3Application:
    return simple_app


@pytest.fixture
async def client(app: ASGI3Application) -> AsyncGenerator[TestClient, Any]:
    async with TestClient(app=app) as client:
        yield client


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


async def test_headers(client: TestClient) -> None:
    header_value = "Some Value"
    resp = await client.get("/headers/", headers={"X-examplE": header_value})
    assert resp.status_code == HTTPStatus.OK

    data = resp.json()
    assert data["x-example"] == header_value


async def test_echo(client: TestClient) -> None:
    resp = await client.post("/echo", json={"items": []})
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"items": []}
