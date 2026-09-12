"""Smoke tests to check built package.

This module is executed before publishing built package to PyPi.
"""

from http import HTTPMethod, HTTPStatus

from dependency_injector import containers

from pulya import Pulya
from pulya.headers import Headers


class ExampleContainer(containers.DeclarativeContainer):
    pass


def test_simple() -> None:
    Pulya(ExampleContainer)


async def test_no_route_returns_404() -> None:
    """Test that a NOT_FOUND response is returned when no route matches."""
    app = Pulya(ExampleContainer)
    # Simulate a request with a non-matching path

    # Simple mock request to avoid complex header handling
    class MockRequest:
        def __init__(self, method: HTTPMethod, path: str) -> None:
            self._method = method
            self._path = path

        @property
        def method(self) -> HTTPMethod:
            return self._method

        @property
        def path(self) -> str:
            return self._path

        @property
        def headers(self) -> Headers:
            return Headers()

        async def get_content(self) -> bytes:
            return b""

    request = MockRequest(method=HTTPMethod.GET, path="/nonexistent")
    response = await app.handle_http_request(request)
    assert response.status == HTTPStatus.NOT_FOUND
    assert response.content == b'{"error":"Not found."}'
    assert response.headers == [("Content-Type", "application/json")]


if __name__ == "__main__":
    test_simple()
