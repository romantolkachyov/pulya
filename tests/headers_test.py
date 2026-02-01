import pytest

from pulya.asgi import ASGIHeaders
from pulya.headers import Headers, ManyStrategy, TooManyHeadersError
from pulya.rsgi import RSGIHeaders

test_header = "X-Test-Header"
expected_value = "expected_VALUE"


@pytest.fixture(params=[ASGIHeaders, RSGIHeaders])
def headers(request: pytest.FixtureRequest) -> Headers:
    # Actually param attribute is available.
    return request.param()  # type: ignore[no-any-return]


def test_simple(headers: Headers) -> None:
    assert headers.get("unknown-header") is None
    assert headers.get("unknown-header", expected_value) == expected_value

    headers.add(test_header.upper(), expected_value)
    assert headers[test_header] == expected_value
    assert headers.get(test_header.lower()) == expected_value
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

    # TODO @roman: check warning emitted
    assert headers.get(test_header) == headers.get_first(test_header)

    with pytest.raises(TooManyHeadersError):
        headers.get(test_header, None, ManyStrategy.forbid)

    headers.set_list(test_header, [expected_value, new_value])
    assert headers.get_list(test_header) == [expected_value, new_value]
