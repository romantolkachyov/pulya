"""Smoke tests to check built package.

This module is executed before publishing built package to PyPi.
"""

from http import HTTPMethod, HTTPStatus

from dependency_injector import containers

from pulya import Pulya
from pulya.headers import Headers
from pulya.responses import Response


class ExampleContainer(containers.DeclarativeContainer):
    pass


def test_simple() -> None:
    Pulya(ExampleContainer)


async def test_no_pre_encoded_error() -> None:
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
    assert (
        response is not None
    )  # Should return a Response object for ASGI compatibility
    assert response.status == HTTPStatus.NOT_FOUND


def test_pre_encoded_error_response() -> None:
    """Test that pre-encoded error responses are returned correctly."""

    status = HTTPStatus.NOT_FOUND
    response = Response.get_pre_encoded_error_response(status)
    assert response is not None
    assert response.status == status


def test_no_pre_encoded_error_response() -> None:
    """Test that None is returned when no pre-encoded error exists."""

    # Use a clearly non-standard status code (999) not in PRE_ENCODED_ERRORS
    status = 999  # Arbitrary invalid status code
    # Ignore arg type, we can't create HTTPStatus with undefined status
    response = Response.get_pre_encoded_error_response(status)  # type: ignore[arg-type]
    assert response is None


if __name__ == "__main__":
    test_simple()
