from http import HTTPStatus
from typing import ClassVar

import msgspec


class BaseResponse:
    __slots__ = ["headers", "status"]

    def __init__(
        self, status: HTTPStatus, headers: list[tuple[str, str]] | None = None
    ) -> None:
        self.status = status
        self.headers = headers or []


class Response(BaseResponse):
    __slots__ = ["content", "headers", "status"]

    default_content_type = "text/plain"

    def __init__(
        self,
        content: bytes,
        status: HTTPStatus = HTTPStatus.OK,
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(status=status, headers=headers)
        self.headers = headers or []
        self.content = content

    # Pre-encoded common HTTP error responses
    PRE_ENCODED_ERRORS: ClassVar[
        dict[HTTPStatus, tuple[bytes, list[tuple[str, str]]]]
    ] = {
        HTTPStatus.NOT_FOUND: (
            msgspec.json.encode({"error": "Not found."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.BAD_REQUEST: (
            msgspec.json.encode({"error": "Bad request."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.UNAUTHORIZED: (
            msgspec.json.encode({"error": "Unauthorized."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.FORBIDDEN: (
            msgspec.json.encode({"error": "Forbidden."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.METHOD_NOT_ALLOWED: (
            msgspec.json.encode({"error": "Method not allowed."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.UNPROCESSABLE_ENTITY: (
            msgspec.json.encode({"error": "Unprocessable entity."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.TOO_MANY_REQUESTS: (
            msgspec.json.encode({"error": "Too many requests."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.INTERNAL_SERVER_ERROR: (
            msgspec.json.encode({"error": "Internal server error."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.BAD_GATEWAY: (
            msgspec.json.encode({"error": "Bad gateway."}),
            [("Content-Type", "application/json")],
        ),
        HTTPStatus.SERVICE_UNAVAILABLE: (
            msgspec.json.encode({"error": "Service unavailable."}),
            [("Content-Type", "application/json")],
        ),
    }

    @classmethod
    def get_pre_encoded_error_response(cls, status: HTTPStatus) -> "Response | None":
        """
        Retrieve a pre-encoded error response for the given HTTP status.

        Args:
            status (HTTPStatus): The HTTP status code to look up.

        Returns:
            Response | None: A Response object with pre-encoded content and headers,
            or None if not found.
        """
        if status in cls.PRE_ENCODED_ERRORS:
            content, headers = cls.PRE_ENCODED_ERRORS[status]
            return Response(content=content, status=status, headers=headers)
        return None
