from dependency_injector import containers

from pulya import Pulya


class ExampleContainer(containers.DeclarativeContainer):
    pass


def test_simple() -> None:
    Pulya(ExampleContainer)


if __name__ == "__main__":
    test_simple()
