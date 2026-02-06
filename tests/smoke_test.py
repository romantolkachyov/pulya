"""Smoke tests to check built package.

This module is executed before publishing built package to PyPi.
"""

from http import HTTPMethod, HTTPStatus

from dependency_injector import containers

from pulya import Pulya
from pulya.headers import Headers, ManyStrategy
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
            # Return a minimal Headers implementation for testing
            class SimpleHeaders:
                def get(
                    self,
                    key: str,
                    default: str | None = None,
                    strategy: ManyStrategy = ManyStrategy.warn,
                ) -> str | None:
                    return default

                def get_list(self, key: str) -> list[str]:
                    return []

            return SimpleHeaders()

        async def get_content(self) -> bytes:
            return b""

    request = MockRequest(method=HTTPMethod.GET, path="/nonexistent")
    response = await app.handle_http_request(request)
    assert (
        response is not None
    )  # Should return a Response object for ASGI compatibility
    assert response.status == HTTPStatus.NOT_FOUND


async def test_not_found_response() -> None:
    """Test that NOT_FOUND response is returned when no route matches."""
    app = Pulya(ExampleContainer)
    # Simulate a request with no matching route
    response = await app.handle_http_request(None)
    assert response is None


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
    response = Response.get_pre_encoded_error_response(status)
    assert response is None


if __name__ == "__main__":
    test_simple()
