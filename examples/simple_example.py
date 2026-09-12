"""Example app for performance testing."""

from typing import Annotated, Any

import msgspec.json
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from pulya import BearerToken, Body, Depends, Header, Pulya
from pulya.containers import RequestContainer
from pulya.headers import Headers
from pulya.responses import Response


class EchoBodyItem(msgspec.Struct):
    a: str
    b: str
    c: str
    d: str
    e: str
    f: str
    g: str


class EchoBody(msgspec.Struct):
    items: list[EchoBodyItem]


class UserRepo:
    """Example user repository."""

    async def fetch_by_token(self, token: str) -> str:
        return f"user-for-{token}"


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[__name__],
    )

    user_repo = providers.Singleton(UserRepo)


async def get_user(
    token: Annotated[str | None, BearerToken()],
    repo: Annotated[UserRepo, Provide[Container.user_repo]],
) -> str:
    # Just for example of how dependency may look like, no special meaning.
    # Depends() wraps it with the wiring resolver, no @inject is needed.
    if token is None:
        return "<Anonymous>"
    return await repo.fetch_by_token(token)


app = Pulya(Container)


@app.get("/")
async def index() -> dict[str, Any]:
    return {"success": True}


@app.get("/wiring/{name}")
async def two_containers_wiring(
    name: str,
    headers: Annotated[Headers, Provide[RequestContainer.headers]],
    user: str = Depends(get_user),
) -> dict[str, Any]:
    return {"test": "ok", "user": user, "name": name, "headers": list(headers)}


@app.get("/headers/")
async def print_headers(
    x_example: Annotated[str, Header("X-Example")],
) -> dict[str, str]:
    return {"x-example": x_example}


@app.get("/plain_response/")
async def plain_response() -> Response:
    return Response(content=b"Hello in plain text!")


@app.get("/bytes/")
async def bytes_response() -> bytes:
    return b"Hello in plain text!"


@app.get("/str/")
async def str_response() -> str:
    return "Hello in plain text!"


@app.post("/echo")
async def echo(
    body: Annotated[EchoBody, Body(EchoBody)],
) -> EchoBody:
    return body


for i in range(100):
    app.get(f"/some/{{id}}/and/{{another}}/{i}/:other")(index)

app.get("/last_route")(index)
