
"""Safe and deterministic URL normalization."""

from urllib.parse import urlsplit, urlunsplit

MAX_URL_LENGTH = 2048


class URLNormalizationError(ValueError):
    """Raised when a URL cannot be normalized safely."""


def normalize_url(url: str) -> str:
    """Normalize URL structure without removing potentially suspicious evidence.

    URLs without an explicit scheme are interpreted as HTTPS.
    The original path, query, fragment, and authority are preserved.
    No network requests are performed.
    """
    if not isinstance(url, str):
        raise URLNormalizationError("URL must be a string.")

    if not url or not url.strip():
        raise URLNormalizationError("URL cannot be empty.")

    if len(url) > MAX_URL_LENGTH:
        raise URLNormalizationError("URL exceeds the maximum allowed length.")

    if any(character.isspace() for character in url):
        raise URLNormalizationError("URL cannot contain whitespace.")

    candidate = url

    if "://" not in candidate:
        candidate = "https://" + candidate

    try:
        parsed = urlsplit(candidate)

        # Accessing these properties also detects malformed authorities.
        _ = parsed.hostname
        _ = parsed.port

    except ValueError as error:
        raise URLNormalizationError("Malformed URL.") from error

    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc,
            parsed.path,
            parsed.query,
            parsed.fragment,
        )
    )
