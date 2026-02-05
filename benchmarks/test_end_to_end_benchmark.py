"""End-to-end benchmark tests for the Pulya framework."""

from http import HTTPMethod

import pytest
from dependency_injector.containers import DeclarativeContainer
from pytest_benchmark.fixture import BenchmarkFixture

from pulya.routing import Router


class TestContainer(DeclarativeContainer):
    """Test container for benchmarking."""

    __test__ = False


@pytest.mark.benchmark
class TestEndToEndBenchmarks:
    """Benchmark suite for end-to-end request handling."""

    def test_router_creation_benchmark(self, benchmark: BenchmarkFixture) -> None:
        """Benchmark router creation with routes."""

        def create_router() -> Router:
            router = Router()
            router.add_route(HTTPMethod.GET, "/", lambda: "index")
            router.add_route(HTTPMethod.GET, "/users", lambda: "users")
            router.add_route(
                HTTPMethod.GET,
                "/users/{user_id}",
                lambda user_id_param: f"user {user_id_param}",
            )
            return router

        benchmark(create_router)

    def test_route_matching_multiple(self) -> None:
        """Benchmark matching multiple routes."""
        router = Router()
        router.add_route(HTTPMethod.GET, "/", lambda: "index")
        router.add_route(HTTPMethod.GET, "/api/v1/users", lambda: "users")
        router.add_route(HTTPMethod.GET, "/api/v1/posts", lambda: "posts")
        router.add_route(
            HTTPMethod.GET,
            "/api/v1/users/{user_id}",
            lambda user_id_param: f"user {user_id_param}",
        )
        router.add_route(
            HTTPMethod.GET,
            "/api/v1/posts/{post_id}",
            lambda post_id_param: f"post {post_id_param}",
        )

        def match_all_routes() -> None:
            # Simulate matching routes for benchmarking
            user_id = "123"
            post_id = "456"

            router.match_route(HTTPMethod.GET, "/")
            router.match_route(HTTPMethod.GET, "/api/v1/users")
            router.match_route(HTTPMethod.GET, "/api/v1/posts")
            router.match_route(HTTPMethod.GET, f"/api/v1/users/{user_id}")
            router.match_route(HTTPMethod.GET, f"/api/v1/posts/{post_id}")
