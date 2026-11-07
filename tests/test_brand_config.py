
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from brand_config import (
    has_brand_impersonation,
    has_suspicious_tld,
    is_url_shortener,
)


def test_legitimate_paypal_domain_is_not_impersonation():
    assert has_brand_impersonation("www.paypal.com", "paypal.com") == 0


def test_paypal_security_example_is_detected():
    assert (
        has_brand_impersonation(
            "paypal-security-example.com",
            "paypal-security-example.com",
        )
        == 1
    )


def test_google_login_example_is_detected():
    assert (
        has_brand_impersonation(
            "google-login-verification-example.com",
            "example.com",
        )
        == 1
    )


def test_brand_in_subdomain_is_detected():
    assert (
        has_brand_impersonation(
            "paypal.evil-example.com",
            "evil-example.com",
        )
        == 1
    )


def test_unrelated_domain_is_not_brand_impersonation():
    assert has_brand_impersonation("example.com", "example.com") == 0


def test_url_shortener_detection():
    assert is_url_shortener("bit.ly") == 1
    assert is_url_shortener("sub.tinyurl.com") == 1
    assert is_url_shortener("example.com") == 0


def test_suspicious_tld_detection():
    assert has_suspicious_tld("xyz") == 1
    assert has_suspicious_tld("com") == 0
    assert has_suspicious_tld("") == 0
