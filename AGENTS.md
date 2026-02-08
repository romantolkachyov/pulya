# Agent Development Guide
## Requirements After Each Modification

After making ANY code modifications, agents MUST:

1. **Run benchmarks**: `uv run pytest benchmarks/ -v`
   - Ensure all benchmark tests pass
   - Verify benchmark performance is acceptable

2. **Run pre-commit**: `uv run pre-commit run --all-files`
   - Fix all style issues (ruff, mypy, formatting)
   - Ensure no linting errors remain

3. **Check 100% test coverage**: `uv run pytest --cov=pulya --cov-fail-under=100`
   - The project requires 100% test coverage
   - No code coverage regressions allowed
   - If coverage drops below 100%, additional tests must be added

**IMPORTANT**: These checks must pass before any branch can be created or commit made. No exceptions.
This file provides essential information for AI agents working on this codebase.

## Project Overview

**pulya** is a tiny Python web framework focused on performance and modern Python features:
- Uses **msgspec** for validation and serialization
- Uses **dependency-injector** as the DI framework
- Supports **RSGI** and **ASGI** interfaces with first-class **granian** support
- Zero-cost routing with **python-matchit**
- Minimum Python version: **3.12** (uses generics syntax like `class Pulya[T: DeclarativeContainer]`)

## Build/Lint/Test Commands

### Running Tests
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/smoke_test.py

# Run a single test function
uv run pytest tests/smoke_test.py::test_simple

# Run with verbose output
uv run pytest -vv

# Run with coverage (enforced 100%)
uv run pytest --cov=pulya --cov-fail-under=100
```

## Justfile Commands

The project includes a `justfile` for convenient task automation using [just](https://github.com/casey/just).

### Installation
```bash
# Install just (command runner)
cargo install just
# Or on macOS: brew install just
```

### Available Commands

```bash
# List all available commands
just

# Run all tests with coverage
just test

# Run linting and formatting checks
just lint

# Fix all auto-fixable issues
just fix

# Run pre-commit hooks
just pre-commit

# Run benchmarks and save results
just benchmark

# Run benchmarks and compare against baseline
just benchmark-compare

# Run all checks (tests + lint + coverage)
just check

# Clean build artifacts
just clean

# Build the package
just build
```

### Benchmarking with Just

The `just benchmark` command automatically:

1. Runs all benchmarks
2. Generates a timestamped JSON report in `performance-reports/baselines/`
3. Displays summary of results

Example:
```bash
just benchmark
# Output: performance-reports/baselines/baseline-20260205.json
```

To compare against the baseline:
```bash
just benchmark-compare
```

### Linting and Formatting
```bash
# Check all files with ruff
uv run ruff check .

# Check specific file
uv run ruff check src/pulya/pulya.py

# Auto-fix issues
uv run ruff check . --fix

# Format all files
uv run ruff format .

# Format specific file
uv run ruff format src/pulya/pulya.py
```

### Type Checking
```bash
# Type check all packages (strict mode)
uv run mypy src/pulya tests

# Type check specific file
uv run mypy src/pulya/pulya.py
```

### Building
```bash
# Build package with uv
uv build

# Install in editable mode
uv pip install -e .
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

## Code Style Guidelines

### Python Style

#### Indentation and Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: No strict limit, but keep reasonable (PEP 8 recommends 79/99)
- **Quotes**: Double quotes for docstrings, single or double for strings

#### Imports
Group imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import threading
from http import HTTPStatus
from typing import Any

import msgspec
from dependency_injector.containers import DeclarativeContainer

from pulya import RequestContainer
from pulya.routing import Router
```

#### Type Hints
- Use type hints for all function parameters and return values
- Use modern Python 3.12+ generic syntax: `class Pulya[T: DeclarativeContainer]`
- Use `|` union syntax: `T | None` instead of `Optional[T]`
- Mypy runs in **strict mode** - all code must be fully typed

Example:
```python
def __init__(self, container_class: type[T]) -> None:
    self.container_class: type[T] = container_class
    self._di_lock: threading.Lock = threading.Lock()
```

#### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private attributes**: `_leading_underscore`
- **Type variables**: `T`, `K`, `V` (single uppercase letters)

#### Docstrings
- Use triple double quotes for all docstrings
- Keep class docstrings concise, describing the purpose
- Method docstrings should explain the behavior briefly

Example:
```python
class Pulya[T: DeclarativeContainer](Router, RSGIApplication, ASGIApplication):
    """
    Pulya application.

    Base class for web-application implementing ASGI and RSGI interfaces.
    """

    async def handle_http_request(self, request: Request) -> Any:
        """Handle HTTP request and return response."""
```

#### Error Handling
- Use try/finally blocks for resource cleanup
- Return HTTP responses for expected errors (e.g., 404 for missing routes)
- Use specific exception types when raising errors

Example:
```python
token = active_request.set(request)
try:
    # Handle request
    return response
finally:
    active_request.reset(token)
```

#### Async Patterns
- All I/O operations must be async
- Use `async def` for coroutines
- Use `await` for async calls
- Test async code with pytest-asyncio (mode: auto)

### Ruff Configuration
Ruff is configured with `select = ["ALL"]` with these ignores:
- `COM812` - Trailing comma
- `D203`, `D212` - Docstring formatting
- `D` - All pydocstyle rules (disabled)
- `ANN401` - Any type in annotations
- `TD003`, `FIX002` - Todo/fixme rules

Per-file ignores for tests:
- `S101` - Assert statements (allowed in tests)
- `D` - Docstring rules (disabled in tests)

## Project Structure

```
pulya/
├── src/pulya/           # Main source code
│   ├── __init__.py      # Public API exports
│   ├── pulya.py         # Core application class
│   ├── asgi.py          # ASGI interface
│   ├── rsgi.py          # RSGI interface
│   ├── routing.py       # Router implementation
│   ├── containers.py    # DI containers
│   ├── request.py       # Request handling
│   ├── responses.py     # Response building
│   ├── headers.py       # HTTP headers
│   └── params.py        # Parameter parsing
├── tests/               # Test suite
│   ├── smoke_test.py    # Sanity checks
│   ├── rsgi_test.py     # RSGI tests
│   └── examples/        # Example tests
├── examples/            # Usage examples
│   └── simple_example.py
└── pyproject.toml       # Project configuration
```

## Testing Patterns
- Tests use **pytest** with **pytest-asyncio** (auto mode)
- **100% coverage is required** (`--cov-fail-under=100`)
- Tests are in `tests/` directory with `*_test.py` naming
- Use standard `assert` statements
- Create stub/mock classes for protocol testing
- Clean up resources in `finally` blocks

Example test:
```python
def test_simple() -> None:
    """Test basic app creation."""
    Pulya(ExampleContainer)
```

## CI/CD

The project uses GitHub Actions (`.github/workflows/build.yml`):
1. Sets up Python 3.14
2. Installs dependencies
3. Runs linting: `uv run ruff check .`
4. Runs type checking: `uv run mypy src/`
5. Runs tests: `uv run pytest -vv`

## Dependencies

### Runtime Dependencies
- `httpx`
- `dependency-injector`
- `msgspec`
- `python-matchit`
- `asgiref`
- `granian>=2.6.1`

### Development Dependencies
- `mypy>=1.19.1`
- `pre-commit>=4.5.1`
- `pytest>=9.0.2`
- `pytest-asyncio>=1.3.0`
- `pytest-cov>=7.0.0`
- `ruff>=0.14.14`

## Notes
- Use `uv run` prefix for all Python commands to use the virtual environment
- The build system uses `uv_build` backend
- Python 3.12+ generics syntax: `class ClassName[T: Bound]`
- Match statements are used for routing logic
- ContextVars are used for request context management
