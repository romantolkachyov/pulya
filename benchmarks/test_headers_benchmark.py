"""
Benchmark tests for header processing in the Pulya framework.

This module benchmarks performance of HTTP header creation.
"""

import pytest
from pytest_benchmark.fixture import BenchmarkFixture


@pytest.mark.benchmark
class TestHeadersBenchmarks:
    """Benchmark suite for header processing."""

    def test_header_list_creation_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark creating raw header list."""

        def create_headers() -> list[tuple[bytes, bytes]]:
            return [
                (b"content-type", b"application/json"),
                (b"authorization", b"Bearer token123"),
                (b"x-custom-header", b"custom-value"),
            ]

        benchmark(create_headers)

    def test_header_dict_creation_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark creating header dict."""

        def create_header_dict() -> dict[str, str]:
            return {
                "content-type": "application/json",
                "authorization": "Bearer token123",
                "x-custom-header": "custom-value",
            }

        benchmark(create_header_dict)
