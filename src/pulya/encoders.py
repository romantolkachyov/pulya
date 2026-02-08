"""JSON encoder module for Pulya framework.

This module provides JSON encoding using msgspec.
"""

from typing import Any

import msgspec


def encode_json(data: Any) -> bytes:
    """Encode data to JSON using msgspec.

    Args:
        data: Data to encode

    Returns:
        bytes: Encoded JSON data
    """
    return msgspec.json.encode(data)


def get_json_encoder() -> Any:
    """Get a JSON encoder function.

    Returns:
        Function to encode JSON data
    """
    return encode_json


__all__ = ["encode_json", "get_json_encoder"]
