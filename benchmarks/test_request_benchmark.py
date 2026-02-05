"""Benchmark tests for request handling in the Pulya framework."""

from http import HTTPMethod

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from pulya.headers import Headers
from pulya.pulya import active_request


class MockRequest:
    """Mock request for benchmarking."""

    def __init__(self) -> None:
        self.method: HTTPMethod = HTTPMethod("GET")
        self.path: str = "/test"

        self.headers: Headers = Headers()

    async def get_content(self) -> bytes:
        return b""


@pytest.mark.benchmark
class TestRequestBenchmarks:
    """Benchmark suite for request handling."""

    def test_contextvar_set_reset_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark setting and resetting request context."""
        request = MockRequest()

        def set_reset_context() -> None:
            token = active_request.set(request)
            active_request.reset(token)

        benchmark(set_reset_context)
