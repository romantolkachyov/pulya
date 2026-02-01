**pulya** is a tiny python web framework focused on performance and new python features.

<div style="text-align: center;">
    <img src="/logos/horizontal-2.png">
</div>

Features:

- **msgspec** for validation and serialization
- **dependency-injector** as the main and the only DI framework
- **RSGI** and first-class **granian** support
- **free-threading** / **no-gil** python support
- zero-cost routing with **python-matchit**

Minimal supported python version 3.12.

# Quick start

Installation:

```shell
pip install pulya
```

Simple application (`main.py`:

```python
from typing import Any
from pulya import Pulya, RequestContainer
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Wiring configuration.
    # RequestContainer will also use this wiring config.
    wiring_config = containers.WiringConfiguration(
        modules=[__name__],
    )

    # Specially named dependency providing access to active request.
    # Must have exact name `request`, actual container will be injected
    # by the application on startup.
    request = providers.Container(RequestContainer)

app = Pulya(Container)

@app.get("/")
def home() -> dict[str, Any]:
    return {"success": True}
```

Run using granian:

```shell
granian --interface rsgi main:app
```

Check:

```shell
curl http://localhost:8000/
```
