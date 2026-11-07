
"""Configurable brand, URL-shortener and suspicious-TLD indicators."""

import re

# Keys are brand tokens expected in hostname labels.
# Values are legitimate registrable domains for those brands.
BRAND_PROFILES = {
    "paypal": ("paypal.com",),
    "google": ("google.com",),
    "microsoft": ("microsoft.com",),
    "amazon": ("amazon.com",),
    "apple": ("apple.com",),
    "facebook": ("facebook.com",),
    "instagram": ("instagram.com",),
    "netflix": ("netflix.com",),
    "linkedin": ("linkedin.com",),
    "github": ("github.com",),
    "dropbox": ("dropbox.com",),
    "docusign": ("docusign.com",),
    "chase": ("chase.com",),
}

URL_SHORTENER_DOMAINS = frozenset({
    "bit.ly",
    "t.co",
    "tinyurl.com",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "rebrand.ly",
    "cutt.ly",
    "shorturl.at",
    "tiny.cc",
    "lnkd.in",
})

SUSPICIOUS_TLDS = frozenset({
    "click",
    "top",
    "xyz",
    "work",
    "gq",
    "tk",
    "ml",
    "cf",
    "ga",
})


def _is_domain_or_subdomain(hostname: str, domain: str) -> bool:
    hostname = hostname.lower().rstrip(".")
    domain = domain.lower().rstrip(".")
    return hostname == domain or hostname.endswith("." + domain)


def is_url_shortener(hostname: str) -> int:
    """Return 1 when hostname belongs to a configured shortener."""
    return int(
        any(
            _is_domain_or_subdomain(hostname, domain)
            for domain in URL_SHORTENER_DOMAINS
        )
    )


def has_suspicious_tld(public_suffix: str) -> int:
    """Return 1 when the public suffix ends in a configured suspicious TLD."""
    if not public_suffix:
        return 0

    final_label = public_suffix.lower().split(".")[-1]
    return int(final_label in SUSPICIOUS_TLDS)


def has_brand_impersonation(
    hostname: str,
    registrable_domain: str,
) -> int:
    """Detect configured brand tokens outside their legitimate domains.

    This is an indicator only, not a phishing verdict.
    """
    hostname = hostname.lower().rstrip(".")
    registrable_domain = registrable_domain.lower().rstrip(".")

    labels = hostname.split(".")
    tokens = {
        token
        for label in labels
        for token in re.split(r"[-_]", label)
        if token
    }

    for brand, legitimate_domains in BRAND_PROFILES.items():
        if brand not in tokens:
            continue

        if any(
            _is_domain_or_subdomain(hostname, domain)
            or registrable_domain == domain
            for domain in legitimate_domains
        ):
            continue

        return 1

    return 0
