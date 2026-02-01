"""Example app for performance testing."""

from typing import Annotated, Any

import msgspec.json
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pulya import Body, Header, Pulya
from pulya.containers import RequestContainer
from pulya.headers import Headers
from pulya.request import Request
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


def get_user_from_request(request: Request) -> str:
    # Just for example of how dependency may look like, no special meaning.
    return f"<User {request.path}>"


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[__name__],
    )

    request = providers.Container(RequestContainer)

    user = providers.Factory(get_user_from_request, request=request.request)


app = Pulya(Container)


@app.get("/")
async def index() -> dict[str, Any]:
    return {"success": True}


@app.get("/wiring/{name}")
@inject
async def two_containers_wiring(
    user: Annotated[str, Provide[Container.user]],
    name: str,
    headers: Annotated[Headers, Provide[RequestContainer.headers]],
) -> dict[str, Any]:
    return {"test": "ok", "user": user, "name": name, "headers": list(headers)}


@app.get("/headers/")
@inject
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
@inject
async def echo(
    body: Annotated[EchoBody, Body(EchoBody)],
) -> EchoBody:
    return body


for i in range(100):
    app.get(f"/some/{{id}}/and/{{another}}/{i}/:other")(index)

app.get("/last_route")(index)
