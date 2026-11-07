
"""Versioned feature definitions for phishing URL detection."""

FEATURE_SCHEMA_VERSION = "v2"

V1_FEATURES = (
    "has_https",
    "domain_length",
    "num_dots",
    "num_hyphens",
    "num_digits",
    "digit_ratio",
    "has_at_symbol",
    "has_suspicious_word",
    "has_ip_address",
    "num_subdomains",
)

V2_ADDITIONAL_FEATURES = (
    "url_length",
    "hostname_length",
    "path_length",
    "query_param_count",
    "special_char_count",
    "hostname_entropy",
    "has_punycode",
    "has_unicode_hostname",
    "has_percent_encoding",
    "has_malformed_percent_encoding",
    "is_url_shortener",
    "has_suspicious_tld",
    "has_brand_impersonation",
    "hostname_complexity",
    "has_suspicious_keyword_pattern",
)

V2_FEATURES = V1_FEATURES + V2_ADDITIONAL_FEATURES

FEATURE_SCHEMAS = {
    "v1": V1_FEATURES,
    "v2": V2_FEATURES,
}


def get_feature_names(version: str = FEATURE_SCHEMA_VERSION) -> tuple[str, ...]:
    """Return feature names in their deterministic schema order."""
    try:
        return FEATURE_SCHEMAS[version]
    except KeyError as error:
        raise ValueError(f"Unsupported feature schema version: {version}") from error
