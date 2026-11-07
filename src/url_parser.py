
"""Structured URL parsing with offline Public Suffix List support."""

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

import idna
import tldextract

from url_normalizer import normalize_url

# Disable remote PSL downloads. tldextract uses its packaged suffix snapshot.
_EXTRACT_DOMAIN = tldextract.TLDExtract(
    suffix_list_urls=(),
    include_psl_private_domains=True,
)

PERCENT_ENCODING_PATTERN = re.compile(r"%[0-9a-fA-F]{2}")
MALFORMED_PERCENT_ENCODING_PATTERN = re.compile(r"%(?![0-9a-fA-F]{2})")


class URLParsingError(ValueError):
    """Raised when URL parsing cannot be completed safely."""


@dataclass(frozen=True)
class ParsedURL:
    original_url: str
    normalized_url: str
    scheme: str
    hostname: str
    hostname_ascii: str
    hostname_unicode: str
    port: int | None
    path: str
    query: str
    fragment: str
    registrable_domain: str
    public_suffix: str
    is_ip_address: bool
    is_ipv6: bool
    has_unicode_hostname: bool
    has_punycode: bool
    has_credentials: bool
    has_percent_encoding: bool
    has_malformed_percent_encoding: bool


def _convert_hostname(hostname: str) -> tuple[str, str]:
    """Return the ASCII and Unicode representations of a hostname."""
    hostname = hostname.rstrip(".")

    if not hostname:
        raise URLParsingError("Hostname is empty.")

    try:
        ascii_hostname = idna.encode(
            hostname,
            uts46=True,
            std3_rules=True,
        ).decode("ascii").lower()

        unicode_hostname = idna.decode(
            ascii_hostname.encode("ascii"),
            uts46=True,
            std3_rules=True,
        )

    except (idna.IDNAError, UnicodeError) as error:
        raise URLParsingError("Invalid internationalized hostname.") from error

    return ascii_hostname, unicode_hostname


def parse_url(url: str) -> ParsedURL:
    """Parse a URL into a structured, immutable representation.

    This function performs no DNS lookups, HTTP requests, or external
    network operations.
    """
    try:
        normalized = normalize_url(url)
        parsed = urlsplit(normalized)

        hostname = parsed.hostname

        if not hostname:
            raise URLParsingError("URL does not contain a hostname.")

        port = parsed.port
        has_credentials = "@" in parsed.netloc

        try:
            ip_address = ipaddress.ip_address(hostname)
            is_ip_address = True
            is_ipv6 = isinstance(ip_address, ipaddress.IPv6Address)
            ascii_hostname = str(ip_address).lower()
            unicode_hostname = ascii_hostname
        except ValueError:
            is_ip_address = False
            is_ipv6 = False
            ascii_hostname, unicode_hostname = _convert_hostname(hostname)

        has_unicode_hostname = any(ord(char) > 127 for char in hostname)

        has_punycode = any(
            label.lower().startswith("xn--")
            for label in hostname.split(".")
        )

        has_percent_encoding = bool(
            PERCENT_ENCODING_PATTERN.search(normalized)
        )

        has_malformed_percent_encoding = bool(
            MALFORMED_PERCENT_ENCODING_PATTERN.search(normalized)
        )

        registrable_domain = ""
        public_suffix = ""

        if not is_ip_address:
            extracted = _EXTRACT_DOMAIN(ascii_hostname)
            registrable_domain = extracted.top_domain_under_public_suffix
            public_suffix = extracted.suffix

        return ParsedURL(
            original_url=url,
            normalized_url=normalized,
            scheme=parsed.scheme.lower(),
            hostname=hostname,
            hostname_ascii=ascii_hostname,
            hostname_unicode=unicode_hostname,
            port=port,
            path=parsed.path,
            query=parsed.query,
            fragment=parsed.fragment,
            registrable_domain=registrable_domain,
            public_suffix=public_suffix,
            is_ip_address=is_ip_address,
            is_ipv6=is_ipv6,
            has_unicode_hostname=has_unicode_hostname,
            has_punycode=has_punycode,
            has_credentials=has_credentials,
            has_percent_encoding=has_percent_encoding,
            has_malformed_percent_encoding=has_malformed_percent_encoding,
        )

    except URLParsingError:
        raise
    except (ValueError, UnicodeError) as error:
        raise URLParsingError("Unable to parse URL safely.") from error
