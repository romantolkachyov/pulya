"""Tests for JSON encoder module."""

from pulya.encoders import encode_json, get_json_encoder


class TestEncodeJson:
    """Tests for encode_json function."""

    def test_encode_json_basic(self) -> None:
        """Test basic JSON encoding."""
        data = {"key": "value", "number": 42}
        result = encode_json(data)
        assert isinstance(result, bytes)
        assert result == b'{"key":"value","number":42}'

    def test_encode_json_empty_dict(self) -> None:
        """Test encoding empty dictionary."""
        result = encode_json({})
        assert result == b"{}"

    def test_encode_json_list(self) -> None:
        """Test encoding list."""
        data = [1, 2, 3]
        result = encode_json(data)
        assert result == b"[1,2,3]"

    def test_encode_json_string(self) -> None:
        """Test encoding string."""
        result = encode_json("hello")
        assert result == b'"hello"'

    def test_encode_json_none(self) -> None:
        """Test encoding None."""
        result = encode_json(None)
        assert result == b"null"


class TestGetJsonEncoder:
    """Tests for get_json_encoder function."""

    def test_get_json_encoder_returns_callable(self) -> None:
        """Test that get_json_encoder returns a callable."""
        encoder = get_json_encoder()
        assert callable(encoder)

    def test_get_json_encoder_encodes_correctly(self) -> None:
        """Test that the encoder returned by get_json_encoder works."""
        encoder = get_json_encoder()
        data = {"test": "data"}
        result = encoder(data)
        assert isinstance(result, bytes)
        assert result == b'{"test":"data"}'
