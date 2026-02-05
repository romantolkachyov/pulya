<p align="center"><b>pulya</b> is a tiny python web framework focused on performance and new python features.</p>
<div style="text-align: center;">
    <img src="/logos/horizontal-2.png">
</div>
<p></p>

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

---
# Development

## Building from Source

```bash
# Clone the repository
git clone https://github.com/romantolkachyov/pulya.git
cd pulya

# Install dependencies
uv pip install -e ".[dev]"
```

## Using Just (Command Runner)

The project includes a `justfile` for convenient task automation. Install `just` first:

```bash
# macOS
brew install just

# Linux
cargo install just

# Or download from https://github.com/casey/just/releases
```

### Available Commands

```bash
# Run all tests with coverage
just test

# Run linting and type checking
just lint

# Run benchmarks and save results
just benchmark

# Compare current performance against baseline
just benchmark-compare

# Run all checks (tests + lint + coverage)
just check

# Fix auto-fixable linting issues
just fix

# Run pre-commit hooks
just pre-commit

# Build the package
just build

# Clean build artifacts
just clean

# List all commands
just
```

### Performance Benchmarking

Run benchmarks to measure performance:

```bash
# Run benchmarks and generate timestamped report
just benchmark

# Output will be saved to:
# performance-reports/baselines/baseline-YYYYMMDD.json
```

View the baseline report at `performance-reports/baselines/BASELINE.md`.

---

In the actual state with a lack of some features, **pulya** outperforms all frameworks available in
https://github.com/romantolkachyov/python-framework-benchmarks benchmark.

```
Benchmark Results using wrk with 12 threads
        and 400 connections for 10s
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Framework ┃ Requests/sec ┃ Transfer/sec ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ pulya     │ 138690.14    │     21.96MB  │
│ starlette │ 129946.20    │     18.84MB  │
│ litestar  │ 111868.04    │     18.35MB  │
│ sanic     │ 105941.45    │     17.28MB  │
│ fastapi   │  93575.14    │     13.56MB  │
│ quart     │  67418.17    │      9.84MB  │
│ robyn     │  53397.80    │      6.62MB  │
│ flask     │   2232.87    │    388.25KB  │
└───────────┴──────────────┴──────────────┘
```

Uvicorn:

```
wrk -t12 -c400 -d10s -s wrk_script.lua http://localhost:8000/echo
Running 10s test @ http://localhost:8000/echo
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     5.40ms    8.58ms 128.34ms   89.02%
    Req/Sec    11.72k     1.55k   55.05k    92.67%
  1400773 requests in 10.10s, 221.76MB read
Requests/sec: 138690.14
Transfer/sec:     21.96MB
```

Granian:

```
wrk -t12 -c400 -d10s -s wrk_script.lua http://localhost:8000/echo
Running 10s test @ http://localhost:8000/echo
  12 threads and 400 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     8.90ms   14.66ms 133.29ms   89.34%
    Req/Sec     7.51k   833.27    10.94k    69.75%
  896147 requests in 10.00s, 125.63MB read
Requests/sec:  89588.07
Transfer/sec:     12.56MB
```
