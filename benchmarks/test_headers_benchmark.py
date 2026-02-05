"""
Benchmark tests for header processing in the Pulya framework.

This module benchmarks performance of HTTP header parsing and manipulation.
"""

import pytest

# Benchmark header operations without creating Headers objects
# since Headers has a complex initialization


@pytest.mark.benchmark
class TestHeadersBenchmarks:
    """Benchmark suite for header processing."""

    def test_header_list_creation_benchmark(
        self, benchmark: pytest.BenchmarkFixture
    ) -> None:
        """Benchmark creating raw header list."""

        def create_headers():
            return [
                (b"content-type", b"application/json"),
                (b"authorization", b"Bearer token123"),
                (b"x-custom-header", b"custom-value"),
            ]

        benchmark(create_headers)

    def test_header_dict_creation_benchmark(
        self, benchmark: pytest.BenchmarkFixture
    ) -> None:
        """Benchmark creating header dict."""

        def create_header_dict():
            return {
                "content-type": "application/json",
                "authorization": "Bearer token123",
                "x-custom-header": "custom-value",
            }

        benchmark(create_header_dict)
