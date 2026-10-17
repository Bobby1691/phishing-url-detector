"""Validation of user-entered URLs."""

import ipaddress
import re
from urllib.parse import urlparse

MAX_URL_LENGTH = 2048
ERROR_MESSAGE = "Please enter a valid web address, for example https://example.com"

# A domain label: letters, digits, hyphens or underscores, 1 to 63 characters,
# and it must not start or end with a hyphen.
LABEL_PATTERN = re.compile(r"^(?!-)[a-z0-9_-]{1,63}(?<!-)$")

# A top-level domain: two or more letters, or an internationalized "xn--" form.
TLD_PATTERN = re.compile(r"^([a-z]{2,63}|xn--[a-z0-9-]{1,59})$")


class InvalidURLError(ValueError):
    """Raised when the input is not a valid web address."""


def is_valid_url(url):
    """Return True if the text looks like a web address with a domain or IP."""
    if not url or len(url) > MAX_URL_LENGTH or any(ch.isspace() for ch in url):
        return False

    # If the scheme is missing, assume HTTPS (browsers do the same for typed domains).
    full_url = url if "://" in url else "https://" + url
    try:
        parsed = urlparse(full_url)
        host = parsed.hostname
        _ = parsed.port  # Raises ValueError if the port is not a valid number.
    except ValueError:
        return False

    if parsed.scheme.lower() not in ("http", "https") or not host:
        return False

    # A raw IP address is accepted as a host.
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass

    # Convert international names (for example muenchen with an umlaut) to ASCII.
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        return False

    labels = host.lower().split(".")
    if len(labels) < 2 or len(host) > 253:
        return False
    if not TLD_PATTERN.match(labels[-1]):
        return False
    return all(LABEL_PATTERN.match(label) for label in labels)


def validate_url(url):
    """Raise InvalidURLError if the text is not a valid web address."""
    if not is_valid_url(url):
        raise InvalidURLError(ERROR_MESSAGE)
