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

    resp = await client.get(
        f"/wiring/{expected_name}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == HTTPStatus.OK

    data = resp.json()
    assert list(data.keys()) == ["test", "user", "name", "headers"]
    assert data["test"] == "ok"
    assert data["user"] == "user-for-test-token"
    assert data["name"] == expected_name
    assert sorted(k for k, v in data["headers"]) == [
        "accept",
        "accept-encoding",
        "authorization",
        "connection",
        "host",
        "user-agent",
    ]


async def test_two_containers_anonymous_without_token(client: TestClient) -> None:
    resp = await client.get("/wiring/example")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["user"] == "<Anonymous>"


async def test_two_containers_anonymous_with_wrong_scheme(client: TestClient) -> None:
    resp = await client.get(
        "/wiring/example",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["user"] == "<Anonymous>"


async def test_two_containers_anonymous_with_bare_scheme(client: TestClient) -> None:
    resp = await client.get("/wiring/example", headers={"Authorization": "Bearer"})
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["user"] == "<Anonymous>"


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


async def test_bytes_response(client: TestClient) -> None:
    resp = await client.get("/bytes/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.content == b"Hello in plain text!"


async def test_str_response(client: TestClient) -> None:
    resp = await client.get("/str/")
    assert resp.status_code == HTTPStatus.OK
    assert resp.content == b"Hello in plain text!"
