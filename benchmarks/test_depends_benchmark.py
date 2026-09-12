"""Benchmark tests for Depends resolution."""

import asyncio
from http import HTTPMethod

import pytest
from dependency_injector import containers
from pytest_benchmark.fixture import BenchmarkFixture

from benchmarks.config import run_benchmark
from pulya import Depends, Pulya
from pulya.headers import Headers


class MockRequest:
    """Mock request for benchmarking."""

    def __init__(self, path: str) -> None:
        self.method: HTTPMethod = HTTPMethod.GET
        self.path = path
        self.headers: Headers = Headers()

    async def get_content(self) -> bytes:
        return b""


def sync_dependency() -> str:
    """Sync dependency function without markers."""
    return "sync"


async def async_dependency() -> str:
    """Async dependency function without markers."""
    return "async"


class DependsBenchmarkContainer(containers.DeclarativeContainer):
    """Container for Depends benchmarking."""

    __test__ = False

    wiring_config = containers.WiringConfiguration(modules=[__name__])


bench_app = Pulya(DependsBenchmarkContainer)


@bench_app.get("/sync")
async def sync_handler(value: str = Depends(sync_dependency)) -> dict[str, str]:
    return {"value": value}


@bench_app.get("/async")
async def async_handler(value: str = Depends(async_dependency)) -> dict[str, str]:
    return {"value": value}


@bench_app.get("/plain")
async def plain_handler() -> dict[str, bool]:
    return {"success": True}


_event_loop = asyncio.new_event_loop()
_event_loop.run_until_complete(bench_app.on_startup())


@pytest.mark.benchmark
class TestDependsBenchmarks:
    """Benchmark suite for Depends resolution on the request path."""

    def test_depends_sync_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark request handling with a sync Depends parameter."""
        request = MockRequest("/sync")

        def handle() -> None:
            _event_loop.run_until_complete(bench_app.handle_http_request(request))

        run_benchmark(benchmark, handle)

    def test_depends_async_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark request handling with an async Depends parameter."""
        request = MockRequest("/async")

        def handle() -> None:
            _event_loop.run_until_complete(bench_app.handle_http_request(request))

        run_benchmark(benchmark, handle)

    def test_plain_handler_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark request handling without Depends (baseline)."""
        request = MockRequest("/plain")

        def handle() -> None:
            _event_loop.run_until_complete(bench_app.handle_http_request(request))

        run_benchmark(benchmark, handle)
