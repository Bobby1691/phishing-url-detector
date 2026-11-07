
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from validation import (
    MAX_URL_LENGTH,
    InvalidURLError,
    is_valid_url,
    validate_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://example.com/path",
        "example.com",
        "https://192.168.1.1",
        "https://bücher.de",
    ],
)
def test_valid_urls_are_accepted(url):
    assert is_valid_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "",
        " ",
        None,
        123,
        "https://",
        "ftp://example.com",
        "javascript://example.com",
        "https://example.com:99999",
        "https://example.com:invalid",
        "https://example.com path",
        "https://-invalid.com",
        "https://example",
        "x" * (MAX_URL_LENGTH + 1),
    ],
)
def test_invalid_urls_are_rejected(url):
    assert is_valid_url(url) is False


def test_maximum_url_length_is_not_exceeded():
    # A URL exactly at the configured maximum is not rejected
    # merely because of its length. Its remaining syntax is also checked.
    url = "https://example.com/" + (
        "a" * (MAX_URL_LENGTH - len("https://example.com/"))
    )
    assert len(url) == MAX_URL_LENGTH
    assert is_valid_url(url)


def test_validate_url_raises_for_invalid_input():
    with pytest.raises(InvalidURLError):
        validate_url("not a valid URL")


def test_validate_url_accepts_valid_input():
    validate_url("https://example.com")
