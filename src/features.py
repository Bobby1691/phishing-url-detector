"""Feature extraction for the phishing URL detection project.

Only the scheme and the domain part of a URL are analyzed. The training
dataset contains no legitimate URLs with a path or query string, so
path-based features would only teach the model that "has a path" means phishing.
A leading "www." is removed so that "example.com" and "www.example.com"
produce the same features.
"""

import ipaddress
from urllib.parse import urlparse

SUSPICIOUS_WORDS = ["login", "verify", "account", "secure", "update"]

# Domain endings made of two labels. They count as one ending, not as a subdomain.
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


def extract_features(url):
    """Return a dictionary of numeric features extracted from a URL string."""
    features = {}

    # If the scheme is missing, assume HTTPS (browsers do the same for typed domains).
    full_url = url if "://" in url else "https://" + url
    try:
        parsed = urlparse(full_url)
        host = parsed.hostname or ""
        netloc = parsed.netloc
    except ValueError:
        # Malformed URLs (for example an unclosed bracket) cannot be parsed.
        host, netloc = "", ""

    # Treat "www.example.com" and "example.com" as the same site.
    if host.startswith("www."):
        host = host[4:]

    host_length = len(host)

    # Basic structure of the domain.
    features["has_https"] = 1 if full_url.lower().startswith("https") else 0
    features["domain_length"] = host_length
    features["num_dots"] = host.count(".")
    features["num_hyphens"] = host.count("-")

    # Digits in the domain.
    num_digits = sum(ch.isdigit() for ch in host)
    features["num_digits"] = num_digits
    features["digit_ratio"] = num_digits / host_length if host_length else 0

    # An "@" in the network location can hide the real destination.
    features["has_at_symbol"] = 1 if "@" in netloc else 0

    # Flag words that phishing domains often contain.
    features["has_suspicious_word"] = (
        1 if any(word in host.lower() for word in SUSPICIOUS_WORDS) else 0
    )

    # Check whether the host is a raw IP address instead of a domain name.
    try:
        ipaddress.ip_address(host)
        features["has_ip_address"] = 1
    except ValueError:
        features["has_ip_address"] = 0

    # Count subdomains: for "mail.example.com" the parts are mail, example, com.
    if features["has_ip_address"] == 1:
        features["num_subdomains"] = 0
    else:
        parts = host.split(".")
        suffix_length = 2 if ".".join(parts[-2:]) in TWO_PART_SUFFIXES else 1
        features["num_subdomains"] = max(len(parts) - suffix_length - 1, 0)

    return features


if __name__ == "__main__":
    print(extract_features("http://192.168.1.1/login"))
    print(extract_features("https://www.bbc.co.uk/news"))
