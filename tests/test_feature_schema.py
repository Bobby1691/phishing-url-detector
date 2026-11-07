
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from feature_schema import (
    V1_FEATURES,
    V2_FEATURES,
    V2_ADDITIONAL_FEATURES,
    get_feature_names,
)


def test_v1_has_exactly_ten_features():
    assert len(V1_FEATURES) == 10


def test_v1_feature_order_is_preserved():
    assert V1_FEATURES == (
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


def test_v2_contains_all_v1_features_first():
    assert V2_FEATURES[:len(V1_FEATURES)] == V1_FEATURES


def test_v2_has_no_duplicate_features():
    assert len(V2_FEATURES) == len(set(V2_FEATURES))


def test_schema_returns_deterministic_order():
    assert get_feature_names("v1") == V1_FEATURES
    assert get_feature_names("v2") == V2_FEATURES


def test_unsupported_schema_is_rejected():
    with pytest.raises(ValueError):
        get_feature_names("v3")


def test_v2_additional_features_are_present():
    required = {
        "url_length",
        "hostname_length",
        "path_length",
        "query_param_count",
        "hostname_entropy",
        "has_punycode",
        "has_unicode_hostname",
        "has_percent_encoding",
        "has_malformed_percent_encoding",
        "is_url_shortener",
        "has_suspicious_tld",
        "has_brand_impersonation",
        "hostname_complexity",
    }

    assert required.issubset(set(V2_ADDITIONAL_FEATURES))
