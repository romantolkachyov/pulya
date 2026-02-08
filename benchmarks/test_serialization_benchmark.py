"""
Benchmark tests for JSON serialization in the Pulya framework.

This module benchmarks JSON serialization performance with various payload sizes.
"""

import msgspec
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

# Test data for different payload sizes
SMALL_PAYLOAD = {"id": 1, "name": "test"}
MEDIUM_PAYLOAD = {"users": [{"id": i, "name": f"user_{i}"} for i in range(100)]}
LARGE_PAYLOAD = {
    "users": [{"id": i, "name": f"user_{i}", "data": "x" * 100} for i in range(1000)]
}


@pytest.mark.benchmark
class TestSerializationBenchmarks:
    """Benchmark suite for serialization performance."""

    def test_small_json_serialization(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark small JSON payload serialization."""
        encoder = msgspec.json.Encoder()

        def serialize() -> None:
            encoder.encode(SMALL_PAYLOAD)

        benchmark(serialize)

    def test_medium_json_serialization(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark medium JSON payload serialization."""
        encoder = msgspec.json.Encoder()

        def serialize() -> None:
            encoder.encode(MEDIUM_PAYLOAD)

        benchmark(serialize)

    def test_large_json_serialization(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark large JSON payload serialization."""
        encoder = msgspec.json.Encoder()

        def serialize() -> None:
            encoder.encode(LARGE_PAYLOAD)

        benchmark(serialize)
