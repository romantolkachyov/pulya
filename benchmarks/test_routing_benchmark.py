"""
Benchmark tests for route matching in the Pulya framework.

This module benchmarks static and dynamic route matching performance.
"""

from http import HTTPMethod

import pytest

from pulya.routing import Router


@pytest.mark.benchmark
class TestRoutingBenchmarks:
    """Benchmark suite for routing performance."""

    def test_static_route_benchmark(self, benchmark: pytest.BenchmarkFixture) -> None:
        """Benchmark static route matching performance."""
        router = Router()

        # Add static routes using correct API: method, url_pattern, handler
        router.add_route(HTTPMethod.GET, "/", lambda: "index")
        router.add_route(HTTPMethod.GET, "/users", lambda: "users")
        router.add_route(HTTPMethod.GET, "/api/v1/users", lambda: "api users")

        def match_routes():
            router.match_route(HTTPMethod.GET, "/")
            router.match_route(HTTPMethod.GET, "/users")
            router.match_route(HTTPMethod.GET, "/api/v1/users")

        benchmark(match_routes)

    def test_dynamic_route_benchmark(self, benchmark: pytest.BenchmarkFixture) -> None:
        """Benchmark dynamic route matching performance."""
        router = Router()

        # Add dynamic routes with multiple parameters
        router.add_route(
            HTTPMethod.GET, "/users/{user_id}", lambda user_id: f"user {user_id}"
        )
        router.add_route(
            HTTPMethod.GET,
            "/posts/{post_id}/comments/{comment_id}",
            lambda post_id, comment_id: f"post {post_id} comment {comment_id}",
        )

        def match_dynamic_routes():
            router.match_route(HTTPMethod.GET, "/users/123")
            router.match_route(HTTPMethod.GET, "/posts/456/comments/789")

        benchmark(match_dynamic_routes)
