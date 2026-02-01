import pytest

from pulya.asgi import ASGIHeaders
from pulya.headers import ManyStrategy, TooManyHeadersError


def test_simple() -> None:
    headers = ASGIHeaders([])

    test_header = "X-Test-Header"
    expected_value = "expected_VALUE"

    headers.add(test_header, expected_value)
    assert headers[test_header] == expected_value
    assert headers.get(test_header) == expected_value
    assert headers.get_list(test_header) == [expected_value]

    new_value = "new_value"
    headers.set(test_header, new_value)
    assert headers.get(test_header) == new_value
    assert headers.get(test_header) == new_value
    assert headers.get_list(test_header) == [new_value]

    headers.add(test_header, expected_value)
    assert headers.get_first(test_header) == new_value
    assert headers.get_last(test_header) == expected_value
    assert headers.get_list(test_header) == [new_value, expected_value]

    with pytest.raises(TooManyHeadersError):
        headers.get(test_header, None, ManyStrategy.forbid)
