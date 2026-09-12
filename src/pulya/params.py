import warnings
from collections.abc import Callable, Coroutine
from inspect import signature as inspect_signature
from types import UnionType
from typing import Any, get_args, get_type_hints, overload

from dependency_injector.wiring import DIWiringWarning, Provide, inject

from pulya.containers import RequestContainer


def _has_markers(fn: Callable[..., Any]) -> bool:
    """Check if callable signature contains dependency-injector markers."""
    try:
        signature = inspect_signature(fn)
    except (TypeError, ValueError):
        return False
    for param in signature.parameters.values():
        if getattr(param.default, "__IS_MARKER__", False):
            return True
    try:
        hints = get_type_hints(fn, include_extras=True)
    except Exception:  # noqa: BLE001 - unresolvable forward refs
        hints = {}
    for hint in hints.values():
        if any(getattr(arg, "__IS_MARKER__", False) for arg in get_args(hint)[1:]):
            return True
    return False


def _wrap_marked(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap fn with wiring resolver if it has DI markers.

    The wrapper is created at import time, so the Depends marker holds
    a resolving reference instead of the raw function.
    """
    if not _has_markers(fn):
        return fn
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DIWiringWarning)
        return inject(fn)


class _Depends:
    """Marker for a handler parameter resolved by calling fn per request.

    fn is wrapped with the dependency-injector wiring resolver on the
    marker creation, so its Provide markers are resolved from the wired
    containers at startup.
    """

    __slots__ = ("fn",)

    def __init__(self, fn: Callable[..., Any]) -> None:
        self.fn = fn


@overload
def Depends[T](fn: Callable[..., Coroutine[Any, Any, T]]) -> T: ...
@overload
def Depends[T](fn: Callable[..., T]) -> T: ...
def Depends(fn: Callable[..., Any]) -> Any:  # noqa: N802
    """Declare a handler parameter computed by fn on each request.

    fn is a plain function (sync or async) whose arguments are injected
    by dependency-injector wiring from both application and request
    containers. No @inject decorator is needed on fn.

    The marker can be used either as a parameter default
    (``user: User = Depends(get_user)``) or as Annotated metadata
    (``user: Annotated[User, Depends(get_user)]``).

    The parameter type is checked against fn's return type by mypy.
    """
    return _Depends(_wrap_marked(fn))


def Body(_type: type | UnionType) -> Any:  # noqa: N802
    return Provide[RequestContainer.body.provided.deserialize.call(_type)]


def Header(name: str, default: None = None) -> Any:  # noqa: N802
    return Provide[RequestContainer.headers.provided.get.call(name, default)]


def BearerToken() -> Any:  # noqa: N802
    """Provide the bearer token from the Authorization header (or None)."""
    return Provide[RequestContainer.bearer_token.provided.extract.call()]
