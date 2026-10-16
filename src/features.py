"""Feature extraction for the phishing URL detection project."""

import ipaddress
from urllib.parse import urlparse


def extract_features(url):
    """Return a dictionary of numeric features extracted from a URL string."""
    features = {}

    # Add a scheme if it is missing so that the URL can be parsed correctly.
    full_url = url if "://" in url else "http://" + url
    host = urlparse(full_url).hostname or ""

    # Basic structure of the URL.
    features["url_length"] = len(url)
    features["has_https"] = 1 if url.startswith("https") else 0

    # Count every character that is not a letter or a digit.
    features["special_chars"] = 0
    for ch in url:
        if not ch.isalnum():
            features["special_chars"] += 1

    # Flag words that phishing URLs often contain.
    words = ["login", "verify", "account", "secure", "update"]
    features["has_suspicious_word"] = 0
    for w in words:
        if w in url.lower():
            features["has_suspicious_word"] = 1

    # Check whether the host is a raw IP address instead of a domain name.
    try:
        ipaddress.ip_address(host)
        features["has_ip_address"] = 1
    except ValueError:
        features["has_ip_address"] = 0

    # Count subdomains: for "www.example.com" the parts are www, example, com.
    if features["has_ip_address"] == 1:
        features["num_subdomains"] = 0
    else:
        parts = host.split(".")
        features["num_subdomains"] = max(len(parts) - 2, 0)

    return features


if __name__ == "__main__":
    print(extract_features("http://192.168.1.1/login"))
    print(extract_features("https://www.google.com"))
