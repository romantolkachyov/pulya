"""
Benchmark configuration module for the Pulya framework.

This module defines benchmark settings, common test data, and categories
for different types of benchmarks (routing, serialization, etc.).
"""

import time
from collections.abc import Callable
from typing import Any

from pytest_benchmark.fixture import BenchmarkFixture

# ========================
# Benchmark Settings
# ========================

# Fixed-iteration benchmarking: pytest-benchmark's automatic calibration
# picks inconsistent iterations-per-round between runs (observed: 1 vs 7),
# which makes results hard to reproduce. Instead we target a fixed round
# duration so the ~42ns mach_absolute_time tick is amortized to ~0.1%,
# plus a manual warmup (pedantic does not warm up on its own).
ROUND_TARGET_SECONDS = 30e-6
MAX_ITERATIONS = 1000
MIN_ROUNDS = 100
MAX_ROUNDS = 20000
# Aim for ~0.5s of total timed sampling per benchmark: with only ~3ms of
# samples (100 rounds x 30us) the mean follows short-lived CPU frequency
# fluctuations instead of settling.
BENCH_TARGET_SECONDS = 0.5


def run_benchmark(benchmark: BenchmarkFixture, func: Callable[[], Any]) -> None:
    """Run a benchmark with calibrated iterations and adaptive rounds.

    Picks the iteration count from a single sample so each timed round lasts
    ~ROUND_TARGET_SECONDS, runs a manual warmup (pedantic does not warm up
    on its own), then times with pedantic for ~BENCH_TARGET_SECONDS total.
    """
    start = time.perf_counter()
    func()
    elapsed = time.perf_counter() - start
    iterations = max(
        1, min(MAX_ITERATIONS, int(ROUND_TARGET_SECONDS / max(elapsed, 1e-9)))
    )
    rounds = max(
        MIN_ROUNDS, min(MAX_ROUNDS, int(BENCH_TARGET_SECONDS / (iterations * elapsed)))
    )
    for _ in range(min(iterations * 10, 2000)):
        func()
    benchmark.pedantic(func, rounds=rounds, iterations=iterations)  # type: ignore[no-untyped-call]


# ========================
# Sample Routes
# ========================

# Static route patterns
STATIC_ROUTES: list[str] = [
    "/",
    "/api/v1/users",
    "/api/v1/users/{user_id}",
    "/api/v2/products/{product_id}/details",
]

# Dynamic route patterns with multiple segments
DYNAMIC_ROUTES: list[str] = [
    "/api/v1/resources/{resource_type}/{id}/items",
    "/api/v2/users/{user_id}/posts/{post_id}",
    "/api/v3/orders/{order_id}/status",
]

# ========================
# Sample Request Data
# ========================

# Sample request headers for different scenarios
SAMPLE_HEADERS: dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer token12345",
    "User-Agent": "PulyaBenchmark/1.0",
}

# Sample request body for serialization benchmarks
SAMPLE_REQUEST_BODY = {
    "user_id": 123,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "is_active": True,
}

# ========================
# Benchmark Categories
# ========================

BENCHMARK_CATEGORIES = {
    "ROUTING": {
        "description": "Benchmark routing performance (static and dynamic routes).",
        "routes": STATIC_ROUTES + DYNAMIC_ROUTES,
    },
    "SERIALIZATION": {
        "description": "Benchmark serialization/deserialization performance.",
        "data": SAMPLE_REQUEST_BODY,
    },
    "REQUEST_HANDLING": {
        "description": "Benchmark request handling and processing.",
        "headers": SAMPLE_HEADERS,
    },
    "HEADER_PROCESSING": {
        "description": "Benchmark header parsing and manipulation.",
        "headers": SAMPLE_HEADERS,
    },
}

# ========================
# Helper Functions
# ========================


def get_sample_route(route_type: str) -> tuple[str, ...]:
    """
    Get a sample route based on the specified type.

    Args:
        route_type (str): Type of route ('static' or 'dynamic').

    Returns:
        tuple: A tuple containing sample routes of the specified type.

    Raises:
        ValueError: If an invalid route type is provided.
    """
    if route_type == "static":
        return tuple(STATIC_ROUTES)
    if route_type == "dynamic":
        return tuple(DYNAMIC_ROUTES)
    error_msg = f"Invalid route type: {route_type}"
    raise ValueError(error_msg)


def get_sample_headers() -> dict[str, str]:
    """
    Get a dictionary of sample headers for benchmarking.

    Returns:
        dict: A dictionary containing sample headers.
    """
    return SAMPLE_HEADERS.copy()
