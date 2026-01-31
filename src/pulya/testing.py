from typing import Any

import httpx
from asgiref.typing import ASGIApplication


class TestClient(httpx.AsyncClient):
    __test__ = False

    def __init__(
        self, app: ASGIApplication, base_url: str = "http://testserver", **kwargs: Any
    ) -> None:
        transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
        super().__init__(transport=transport, base_url=base_url, **kwargs)
