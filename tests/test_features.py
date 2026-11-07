
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from feature_schema import V1_FEATURES, V2_FEATURES
from features import extract_features


def test_default_extraction_uses_v1():
    features = extract_features("https://example.com")

    assert tuple(features.keys()) == V1_FEATURES
    assert len(features) == 10


def test_v1_preserves_original_feature_values():
    features = extract_features("https://www.bbc.co.uk/news")

    assert features["has_https"] == 1
    assert features["domain_length"] == len("bbc.co.uk")
    assert features["num_dots"] == 2
    assert features["has_ip_address"] == 0
    assert features["num_subdomains"] == 0


def test_v2_returns_exactly_25_features():
    features = extract_features(
        "https://example.com",
        schema_version="v2",
    )

    assert tuple(features.keys()) == V2_FEATURES
    assert len(features) == 25


def test_v2_preserves_v1_features_first():
    v1 = extract_features("https://example.com")
    v2 = extract_features("https://example.com", schema_version="v2")

    for name in V1_FEATURES:
        assert v1[name] == v2[name]


def test_url_structure_features():
    url = "https://example.com/login?a=1&b=2"
    features = extract_features(url, schema_version="v2")

    assert features["url_length"] == len(url)
    assert features["hostname_length"] == len("example.com")
    assert features["path_length"] == len("/login")
    assert features["query_param_count"] == 2


def test_empty_query_values_are_counted():
    features = extract_features(
        "https://example.com/?a=&b=2",
        schema_version="v2",
    )

    assert features["query_param_count"] == 2


def test_hostname_entropy_is_finite():
    features = extract_features(
        "https://a1b2c3-example.com",
        schema_version="v2",
    )

    assert features["hostname_entropy"] > 0
    assert features["hostname_entropy"] < 10


def test_repeated_hostname_has_lower_entropy():
    repeated = extract_features(
        "https://aaaaaaa.com",
        schema_version="v2",
    )
    varied = extract_features(
        "https://abcdefg.com",
        schema_version="v2",
    )

    assert repeated["hostname_entropy"] < varied["hostname_entropy"]


def test_punycode_domain_is_detected():
    features = extract_features(
        "https://xn--bcher-kva.de",
        schema_version="v2",
    )

    assert features["has_punycode"] == 1


def test_unicode_hostname_is_detected():
    features = extract_features(
        "https://bücher.de",
        schema_version="v2",
    )

    assert features["has_unicode_hostname"] == 1


def test_encoded_path_is_detected():
    features = extract_features(
        "https://example.com/%2Fadmin",
        schema_version="v2",
    )

    assert features["has_percent_encoding"] == 1
    assert features["has_malformed_percent_encoding"] == 0


def test_malformed_encoding_is_detected():
    features = extract_features(
        "https://example.com/%2F%ZZ",
        schema_version="v2",
    )

    assert features["has_percent_encoding"] == 1
    assert features["has_malformed_percent_encoding"] == 1


def test_shortener_is_detected():
    features = extract_features(
        "https://bit.ly/abc123",
        schema_version="v2",
    )

    assert features["is_url_shortener"] == 1


def test_suspicious_tld_is_detected():
    features = extract_features(
        "https://example.xyz",
        schema_version="v2",
    )

    assert features["has_suspicious_tld"] == 1


def test_brand_impersonation_is_detected():
    features = extract_features(
        "https://paypal-security-example.com/login",
        schema_version="v2",
    )

    assert features["has_brand_impersonation"] == 1


def test_legitimate_brand_domain_is_not_impersonation():
    features = extract_features(
        "https://www.paypal.com/login",
        schema_version="v2",
    )

    assert features["has_brand_impersonation"] == 0


def test_suspicious_keyword_pattern_is_detected():
    features = extract_features(
        "https://example.com/account/verify",
        schema_version="v2",
    )

    assert features["has_suspicious_keyword_pattern"] == 1


def test_suspicious_keyword_is_only_an_indicator():
    features = extract_features(
        "https://legitimate-example.com/login",
        schema_version="v2",
    )

    # Feature extraction produces indicators, not a phishing verdict.
    assert features["has_suspicious_keyword_pattern"] == 1
    assert "verdict" not in features


def test_ip_address_is_detected():
    features = extract_features(
        "http://192.168.1.1/login",
        schema_version="v2",
    )

    assert features["has_ip_address"] == 1


def test_v2_subdomain_count_uses_public_suffix_list():
    features = extract_features(
        "https://mail.shop.example.co.uk",
        schema_version="v2",
    )

    assert features["num_subdomains"] == 2


def test_non_string_input_is_rejected():
    with pytest.raises(TypeError):
        extract_features(None)


def test_unsupported_schema_is_rejected():
    with pytest.raises(ValueError):
        extract_features("https://example.com", schema_version="v3")


def test_empty_v2_url_is_rejected():
    with pytest.raises(ValueError):
        extract_features("", schema_version="v2")


def test_v2_features_are_numeric_and_finite():
    features = extract_features(
        "https://example.com/path?a=1",
        schema_version="v2",
    )

    assert all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        for value in features.values()
    )

    assert all(
        value == value and abs(value) != float("inf")
        for value in features.values()
    )
