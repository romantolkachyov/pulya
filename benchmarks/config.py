"""
Benchmark configuration module for the Pulya framework.

This module defines benchmark settings, common test data, and categories
for different types of benchmarks (routing, serialization, etc.).
"""


# ========================
# Benchmark Settings
# ========================

WARMUP_ITERATIONS = 5
MIN_ROUNDS = 10
MAX_TIME = 1.0  # seconds per benchmark

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
    raise ValueError(f"Invalid route type: {route_type}")


def get_sample_headers() -> dict[str, str]:
    """
    Get a dictionary of sample headers for benchmarking.

    Returns:
        dict: A dictionary containing sample headers.
    """
    return SAMPLE_HEADERS.copy()
