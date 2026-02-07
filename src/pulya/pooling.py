from collections import deque  # pragma: no cover
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class ObjectPool[T]:
    """
    Simple generic object pool.

    Provides acquire() and release() methods for object reuse to reduce GC pressure.
    """

    def __init__(self, factory: Callable[[], T], max_size: int = 100) -> None:
        self._factory = factory
        self._max_size = max_size
        self._pool: deque[T] = deque()
        self._active_count = 0

    def acquire(self) -> T:
        """Acquire an object from the pool or create a new one."""
        obj = self._pool.pop() if self._pool else self._factory()
        self._active_count += 1
        return obj

    def release(self, obj: T) -> None:
        """Return an object to the pool."""
        if len(self._pool) < self._max_size:
            # Reset the object state before returning it to the pool
            self._reset_object(obj)
            self._pool.append(obj)
        else:
            # Pool is at max size, discard the object
            pass  # pragma: no cover
        self._active_count -= 1

    def _reset_object(self, obj: T) -> None:
        """Reset object to initial state.

        Override in subclasses for custom reset logic.
        """
        # Default implementation does nothing - override as needed

    @property
    def pool_size(self) -> int:
        return len(self._pool)

    @property
    def active_count(self) -> int:
        return self._active_count

    def clear(self) -> None:
        """Clear the pool, discarding all pooled objects."""
        self._pool.clear()
        self._active_count = 0
