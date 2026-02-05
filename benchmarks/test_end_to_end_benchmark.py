"""End-to-end benchmark tests for the Pulya framework."""

from http import HTTPMethod

import pytest
from dependency_injector.containers import DeclarativeContainer

from pulya.routing import Router


class TestContainer(DeclarativeContainer):
    """Test container for benchmarking."""


@pytest.mark.benchmark
class TestEndToEndBenchmarks:
    """Benchmark suite for end-to-end request handling."""

    def test_router_creation_benchmark(
        self, benchmark: pytest.BenchmarkFixture
    ) -> None:
        """Benchmark router creation with routes."""

        def create_router():
            router = Router()
            router.add_route(HTTPMethod.GET, "/", lambda: "index")
            router.add_route(HTTPMethod.GET, "/users", lambda: "users")
            router.add_route(HTTPMethod.GET, "/users/{id}", lambda id: f"user {id}")
            return router

        benchmark(create_router)

    def test_route_matching_multiple(self, benchmark: pytest.BenchmarkFixture) -> None:
        """Benchmark matching multiple routes."""
        router = Router()
        router.add_route(HTTPMethod.GET, "/", lambda: "index")
        router.add_route(HTTPMethod.GET, "/api/v1/users", lambda: "users")
        router.add_route(HTTPMethod.GET, "/api/v1/posts", lambda: "posts")
        router.add_route(HTTPMethod.GET, "/api/v1/users/{id}", lambda id: f"user {id}")
        router.add_route(HTTPMethod.GET, "/api/v1/posts/{id}", lambda id: f"post {id}")

        def match_all_routes():
            router.match_route(HTTPMethod.GET, "/")
            router.match_route(HTTPMethod.GET, "/api/v1/users")
            router.match_route(HTTPMethod.GET, "/api/v1/posts")
            router.match_route(HTTPMethod.GET, "/api/v1/users/123")
            router.match_route(HTTPMethod.GET, "/api/v1/posts/456")

        benchmark(match_all_routes)
