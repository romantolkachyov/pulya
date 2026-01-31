"""Example app for performance testing."""

from typing import Annotated, Any

import msgspec.json
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from pulya.application import Pulya
from pulya.containers import RequestContainer
from pulya.headers import Headers
from pulya.request import Request


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
    return f"<User {request.path}>"


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[__name__],
    )

    request = providers.Container(RequestContainer)

    user = providers.Factory(get_user_from_request, request=request.request)


app = Pulya(Container)


@app.get("/")
async def index() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/test/{name}")
@inject
async def test(
    user: Annotated[str, Provide[Container.user]],
    name: str,
    headers: Annotated[Headers, Provide[RequestContainer.headers]],
) -> dict[str, Any]:
    return {"test": "ok", "user": user, "name": name, "headers": list(headers)}


@app.post("/echo")
@inject
async def echo(
    body: Annotated[
        EchoBody, Provide[RequestContainer.body.provided.deserialize.call(EchoBody)]
    ],
) -> EchoBody:
    return body


for i in range(100):
    app.get(f"/some/{{id}}/and/{{another}}/{i}/:other")(index)

app.get("/last_route")(index)
