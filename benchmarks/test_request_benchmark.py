"""
Benchmark tests for request handling in the Pulya framework.

This module benchmarks performance of request context management.
"""

import pytest

from pulya.pulya import active_request


@pytest.mark.benchmark
class TestRequestBenchmarks:
    """Benchmark suite for request handling."""

    def test_contextvar_set_reset_benchmark(
        self, benchmark: pytest.BenchmarkFixture
    ) -> None:
        """Benchmark setting and resetting request context."""

        class MockRequest:
            """Mock request for benchmarking."""

            method = "GET"
            path = "/test"

        request = MockRequest()

        def set_reset_context():
            token = active_request.set(request)
            active_request.reset(token)

        benchmark(set_reset_context)
