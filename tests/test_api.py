"""API integration and network-safety tests."""

import socket
import sys
import urllib.request
from pathlib import Path

import requests
from fastapi.testclient import TestClient

# Add the project's src directory to the Python import path.
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import api
from features import extract_features
from url_parser import parse_url


client = TestClient(api.app)

def test_analyze_valid_url_preserves_response_contract():
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/login?next=home"},
    )

    assert response.status_code == 200

    body = response.json()

    # Preserve the existing public API response contract.
    assert set(body) == {"verdict", "risk_score", "reasons"}
    assert body["verdict"] in {"Phishing", "Suspicious", "Unverified"}
    assert isinstance(body["risk_score"], (int, float))
    assert 0 <= body["risk_score"] <= 100
    assert isinstance(body["reasons"], list)


def test_analyze_invalid_url_returns_http_400():
    response = client.post(
        "/analyze",
        json={"url": "https://"},
    )

    assert response.status_code == 400
    assert "detail" in response.json()


def test_analyze_whitespace_url_returns_http_400():
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/path with spaces"},
    )

    assert response.status_code == 400
    assert "detail" in response.json()


def test_analyze_missing_url_returns_http_422():
    response = client.post("/analyze", json={})

    assert response.status_code == 422


def test_v2_feature_extraction_does_not_make_network_requests(monkeypatch):
    """Parsing and feature extraction must work without network access."""

    def reject_network(*args, **kwargs):
        raise AssertionError("Unexpected network request during URL analysis.")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(urllib.request, "urlopen", reject_network)
    monkeypatch.setattr(
        requests.sessions.Session,
        "request",
        reject_network,
    )

    parsed = parse_url("https://sub.example.co.uk/path?next=login")

    features = extract_features(
        "https://sub.example.co.uk/path?next=login",
        schema_version="v2",
    )

    assert parsed.hostname_ascii == "sub.example.co.uk"
    assert features["num_subdomains"] == 1
    assert features["has_suspicious_keyword_pattern"] == 1
