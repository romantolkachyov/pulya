"""
JSON encoder module for Pulya framework.

This module provides a fast JSON encoder that tries to use orjson if available,
falling back to msgspec for compatibility.
"""

from collections.abc import Callable
from typing import Any

try:
    import orjson

    ORJSON_AVAILABLE = True
except ImportError:  # pragma: no cover
    ORJSON_AVAILABLE = False  # pragma: no cover

try:
    import msgspec

    MSGSPEC_AVAILABLE = True
except ImportError:  # pragma: no cover
    MSGSPEC_AVAILABLE = False  # pragma: no cover

# Cache for encoded responses
_encoded_cache: dict[tuple[Any, bool], bytes] = {}
_CACHE_SIZE = 1000


def encode_json(data: Any, *, use_orjson: bool | None = None) -> bytes:
    """
    Encode data to JSON using orjson if available, falling back to msgspec.

    Args:
        data: Data to encode
        use_orjson: Explicitly specify whether to use orjson. If None (default),
                   uses orjson if available.

    Returns:
        bytes: Encoded JSON data
    """
    # Determine if we should use orjson
    if use_orjson is None:
        use_orjson = ORJSON_AVAILABLE

    # If caching enabled and data is hashable, check cache first
    cache_key = (id(data), use_orjson)
    if cache_key in _encoded_cache:
        return _encoded_cache[cache_key]

    # Try orjson first
    if use_orjson:
        try:
            # Use orjson with default settings for fast encoding
            encoded = orjson.dumps(data)
            # Store in cache
            if len(_encoded_cache) < _CACHE_SIZE:  # pragma: no cover
                _encoded_cache[cache_key] = encoded
            return encoded  # noqa: TRY300  # noqa: TRY300
        except Exception:  # pragma: no cover  # noqa: S110 BLE001
            # Fall back to msgspec if orjson fails
            pass
    # Fall back to msgspec
    try:
        encoded = msgspec.json.encode(data)
        # Store in cache
        if len(_encoded_cache) < _CACHE_SIZE:  # pragma: no cover
            _encoded_cache[cache_key] = encoded
        return encoded  # noqa: TRY300
    except Exception as e:  # pragma: no cover
        error_msg = f"Failed to encode JSON data: {e}"
        raise RuntimeError(error_msg) from e


def get_json_encoder(*, use_orjson: bool | None = None) -> Callable[..., Any]:
    """
    Get a JSON encoder function that uses orjson if available, falling back to msgspec.

    Args:
        use_orjson: Explicitly specify whether to use orjson. If None (default),
                   uses orjson if available.

    Returns:
        callable: Function to encode JSON data
    """
    return lambda data, *, use_orjson=use_orjson: encode_json(
        data, use_orjson=use_orjson
    )


# Export the encoder function for easy import
__all__ = ["encode_json", "get_json_encoder"]
