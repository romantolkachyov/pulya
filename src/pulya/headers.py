import logging
from collections import defaultdict
from collections.abc import Iterator
from enum import Enum

logger = logging.getLogger(__name__)


class ManyStrategy(Enum):
    first = 1
    last = 2
    warn = 3
    forbid = 4


class Headers:
    """
    HTTP headers.

    An interface for accessing request headers, abstracted from the implementation
    details of a particular protocol.
    """

    __slots__ = ["_headers"]

    _headers: defaultdict[str, list[str]]

    def __getattr__(self, item: str) -> str | None:
        return self.get(item)

    def __iter__(self) -> Iterator[tuple[str, str]]:
        for k in self._headers:
            for v in self._headers[k]:
                yield k, v

    def get(
        self,
        key: str,
        default: str | None = None,
        strategy: ManyStrategy = ManyStrategy.warn,
    ) -> str | None:
        """
        Get header value by name.

        Produce warning log if there are more than one header with the same name.
        This behavior can be changed with `strategy` argument.
        It is better to use dedicated methods like :py:meth:`get_first`,
        :py:meth:`get_last` or :py:meth:`get_list` to avoid warnings
        if multiple headers expected.
        """
        key = key.lower()
        values = self.get_list(key)
        if values is None or len(values) == 0:
            return default
        if len(values) == 1:
            return values[0]

        match strategy:
            case ManyStrategy.first:
                return values[0]
            case ManyStrategy.last:
                return values[-1]
            case ManyStrategy.warn:
                logger.warning("Multiple %s headers received", key)
                return values[0]
            case ManyStrategy.forbid:
                msg = f"Multiple headers `{key}` are forbidden by fail strategy."
                raise ValueError(msg)

    def get_first(self, key: str, default: str | None = None) -> str | None:
        return self.get(key, default, ManyStrategy.first)

    def get_last(self, key: str, default: str | None = None) -> str | None:
        return self.get(key, default, ManyStrategy.last)

    def add(self, key: str, value: str) -> None:
        self._headers[key.lower()].append(value)

    def set(self, key: str, value: str) -> None:
        self._headers[key.lower()] = [value]

    def get_list(self, key: str) -> list[str]:
        return self._headers.get(key.lower(), [])

    def set_list(self, key: str, values: list[str]) -> None:
        self._headers[key.lower()] = values
