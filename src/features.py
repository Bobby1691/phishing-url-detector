
"""Versioned URL feature extraction for phishing detection."""

import ipaddress
import math
import re
from collections import Counter
from urllib.parse import parse_qsl, unquote, urlparse

from brand_config import (
    has_brand_impersonation,
    has_suspicious_tld,
    is_url_shortener,
)
from feature_schema import get_feature_names
from url_parser import parse_url

SUSPICIOUS_WORDS = (
    "login",
    "verify",
    "account",
    "secure",
    "update",
)

SUSPICIOUS_KEYWORDS = frozenset({
    "login",
    "logon",
    "signin",
    "verify",
    "verification",
    "account",
    "secure",
    "security",
    "update",
    "password",
    "passwd",
    "wallet",
    "billing",
    "payment",
    "confirm",
    "support",
    "auth",
    "credential",
    "recover",
    "webscr",
})

# Retained for exact compatibility with the original V1 subdomain calculation.
TWO_PART_SUFFIXES = {
    "co.uk",
    "org.uk",
    "ac.uk",
    "gov.uk",
    "com.au",
    "co.in",
    "co.jp",
    "com.br",
}


def _extract_v1_features(url: str) -> dict:
    """Extract the original ten features without changing their semantics."""
    features = {}

    full_url = url if "://" in url else "https://" + url

    try:
        parsed = urlparse(full_url)
        host = parsed.hostname or ""
        netloc = parsed.netloc
    except ValueError:
        host, netloc = "", ""

    if host.startswith("www."):
        host = host[4:]

    host_length = len(host)

    features["has_https"] = (
        1 if full_url.lower().startswith("https") else 0
    )
    features["domain_length"] = host_length
    features["num_dots"] = host.count(".")
    features["num_hyphens"] = host.count("-")

    num_digits = sum(ch.isdigit() for ch in host)
    features["num_digits"] = num_digits
    features["digit_ratio"] = (
        num_digits / host_length if host_length else 0
    )

    features["has_at_symbol"] = 1 if "@" in netloc else 0

    features["has_suspicious_word"] = int(
        any(word in host.lower() for word in SUSPICIOUS_WORDS)
    )

    try:
        ipaddress.ip_address(host)
        features["has_ip_address"] = 1
    except ValueError:
        features["has_ip_address"] = 0

    if features["has_ip_address"] == 1:
        features["num_subdomains"] = 0
    else:
        parts = host.split(".")
        suffix_length = (
            2 if ".".join(parts[-2:]) in TWO_PART_SUFFIXES else 1
        )
        features["num_subdomains"] = max(
            len(parts) - suffix_length - 1,
            0,
        )

    return features


def _hostname_entropy(hostname: str) -> float:
    """Calculate Shannon entropy in bits per character."""
    if not hostname:
        return 0.0

    counts = Counter(hostname)
    length = len(hostname)

    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )

    return round(entropy, 6)


def _has_suspicious_keyword_pattern(url: str) -> int:
    """Detect suspicious keyword tokens in the URL without fetching it."""
    decoded = unquote(url).lower()
    tokens = set(re.findall(r"[a-z0-9]+", decoded))

    return int(bool(tokens & SUSPICIOUS_KEYWORDS))


def _extract_v2_features(url: str) -> dict:
    """Extract the original features plus advanced URL characteristics."""
    parsed_url = parse_url(url)

    # Keep all original features and their established ordering.
    features = _extract_v1_features(url)

    hostname = parsed_url.hostname_ascii
    original_hostname = parsed_url.hostname

    # V2 uses the Public Suffix List for more accurate subdomain counting.
    if parsed_url.registrable_domain:
        hostname_labels = hostname.split(".")
        registrable_labels = parsed_url.registrable_domain.split(".")

        features["num_subdomains"] = max(
            len(hostname_labels) - len(registrable_labels),
            0,
        )

    hostname_length = len(hostname)

    # The ratio of digits, hyphens and dots provides a simple,
    # deterministic hostname complexity indicator.
    complexity_characters = sum(
        char.isdigit() or char in "-."
        for char in hostname
    )

    hostname_complexity = (
        complexity_characters / hostname_length
        if hostname_length
        else 0.0
    )

    special_char_count = sum(
        not character.isalnum()
        for character in url
    )

    features.update({
        "url_length": len(url),
        "hostname_length": hostname_length,
        "path_length": len(parsed_url.path),
        "query_param_count": len(
            parse_qsl(
                parsed_url.query,
                keep_blank_values=True,
            )
        ),
        "special_char_count": special_char_count,
        "hostname_entropy": _hostname_entropy(hostname),
        "has_punycode": int(parsed_url.has_punycode),
        "has_unicode_hostname": int(
            parsed_url.has_unicode_hostname
        ),
        "has_percent_encoding": int(
            parsed_url.has_percent_encoding
        ),
        "has_malformed_percent_encoding": int(
            parsed_url.has_malformed_percent_encoding
        ),
        "is_url_shortener": is_url_shortener(hostname),
        "has_suspicious_tld": has_suspicious_tld(
            parsed_url.public_suffix
        ),
        "has_brand_impersonation": has_brand_impersonation(
            hostname,
            parsed_url.registrable_domain,
        ),
        "hostname_complexity": round(
            hostname_complexity,
            6,
        ),
        "has_suspicious_keyword_pattern": (
            _has_suspicious_keyword_pattern(url)
        ),
    })

    return features


def extract_features(
    url: str,
    schema_version: str = "v1",
) -> dict:
    """Extract numeric URL features using the requested schema.

    Args:
        url: URL string to analyze.
        schema_version: "v1" for the original ten features or
            "v2" for the expanded 25-feature schema.

    Returns:
        Dictionary containing numeric features in deterministic order.

    Raises:
        TypeError: If URL is not a string.
        ValueError: If the schema is unsupported or V2 parsing fails.
    """
    if not isinstance(url, str):
        raise TypeError("URL must be a string.")

    expected_features = get_feature_names(schema_version)

    if schema_version == "v1":
        features = _extract_v1_features(url)
    elif schema_version == "v2":
        features = _extract_v2_features(url)
    else:
        raise ValueError(
            f"Unsupported feature schema version: {schema_version}"
        )

    if tuple(features.keys()) != expected_features:
        raise RuntimeError(
            f"Feature order does not match schema {schema_version}."
        )

    if not all(
        isinstance(value, (int, float)) and math.isfinite(value)
        for value in features.values()
    ):
        raise RuntimeError("Feature extraction produced invalid values.")

    return features


if __name__ == "__main__":
    example = "https://paypal-security-example.com/login?account=123"

    print("V1:")
    print(extract_features(example))

    print("\nV2:")
    print(extract_features(example, schema_version="v2"))
