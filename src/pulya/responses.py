from http import HTTPStatus
from typing import AsyncGenerator


class BaseResponse:
    __slots__ = ["status", "headers"]

    def __init__(
        self, status: HTTPStatus, headers: list[tuple[str, str]] | None = None
    ) -> None:
        self.status = status
        self.headers = headers or []


class Response(BaseResponse):
    __slots__ = ["status", "content", "headers"]

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


class StreamingResponse(BaseResponse):
    def __init__(
        self,
        stream: AsyncGenerator[bytes],
        status: HTTPStatus = HTTPStatus.OK,
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        super().__init__(status=status, headers=headers)
        self.stream = stream

    def get_content_stream(self) -> AsyncGenerator[bytes, None]:
        return self.stream
