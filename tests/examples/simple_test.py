from http import HTTPStatus

from examples.simple import simple_app
from pulya import TestClient


async def test_simple() -> None:
    assert simple_app

    async with TestClient(simple_app) as client:
        resp = await client.get("/")
        assert resp.status_code == HTTPStatus.OK
