from asyncio import Queue, Task, get_running_loop
from types import TracebackType
from typing import Any, Self

import httpx
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveEvent,
    ASGISendEvent,
    ASGIVersions,
    LifespanScope,
    LifespanShutdownEvent,
    LifespanStartupEvent,
)


async def _lifespan_task(
    app: ASGI3Application,
    input_queue: Queue[ASGIReceiveEvent],
    output_queue: Queue[ASGISendEvent],
) -> None:
    lifespan_scope = LifespanScope(
        type="lifespan",
        asgi=ASGIVersions(spec_version="3.0", version="3.0"),
    )
    await app(
        lifespan_scope,
        input_queue.get,
        output_queue.put,
    )


class TestClient(httpx.AsyncClient):
    __test__ = False
    _lifespan_task: Task[None] | None = None

    def __init__(
        self, app: ASGI3Application, base_url: str = "http://testserver", **kwargs: Any
    ) -> None:
        self._app = app
        transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
        super().__init__(transport=transport, base_url=base_url, **kwargs)

        self._receive_queue: Queue[ASGIReceiveEvent] = Queue()
        self._send_queue: Queue[ASGISendEvent] = Queue()

    async def __aenter__(self) -> Self:
        self._lifespan_task = get_running_loop().create_task(
            _lifespan_task(self._app, self._receive_queue, self._send_queue)
        )
        await self._receive_queue.put(LifespanStartupEvent(type="lifespan.startup"))
        await self._send_queue.get()
        return await super().__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self._receive_queue.put(LifespanShutdownEvent(type="lifespan.shutdown"))
        await self._send_queue.get()
        if self._lifespan_task is not None:
            await self._lifespan_task
        await super().__aexit__(exc_type, exc_value, traceback)
