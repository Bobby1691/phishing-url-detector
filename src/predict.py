"""Analyze a URL with the trained model and explain the result."""

import pandas as pd
from xgboost import XGBClassifier

from features import extract_features
from validation import InvalidURLError, validate_url

MODEL_PATH = "models/phishing_model.json"

# Risk score cutoffs (in percent), chosen with src/threshold_report.py.
SUSPICIOUS_THRESHOLD = 40.0
PHISHING_THRESHOLD = 80.0


def load_model():
    """Load the trained model from disk."""
    model = XGBClassifier()
    model.load_model(MODEL_PATH)
    return model


def get_reasons(features):
    """Return human-readable warning signs found in the URL features."""
    reasons = []
    if features["has_ip_address"] == 1:
        reasons.append("The address uses a raw IP number instead of a domain name.")
    if features["has_https"] == 0:
        reasons.append("The connection is not secured with HTTPS.")
    if features["has_suspicious_word"] == 1:
        reasons.append(
            "The domain contains words often seen in phishing links (such as login or verify)."
        )
    if features["has_at_symbol"] == 1:
        reasons.append("The URL contains an @ symbol, which can hide the real destination.")
    if features["domain_length"] > 30:
        reasons.append("The domain name is unusually long.")
    if features["num_hyphens"] >= 3:
        reasons.append("The domain contains many hyphens.")
    if features["num_subdomains"] >= 3:
        reasons.append("The domain has many subdomains.")
    return reasons


def analyze_url(model, url):
    """Return the verdict, risk score and reasons for a single URL.

    The verdict is "Phishing", "Suspicious" or "Legitimate".
    Raises InvalidURLError if the text is not a valid web address.
    """
    url = url.strip()
    validate_url(url)

    features = extract_features(url)
    X = pd.DataFrame([features])

    # Column 0 of predict_proba is label 0 (phishing), column 1 is label 1 (legitimate).
    phishing_probability = model.predict_proba(X)[0][0]
    risk_score = round(float(phishing_probability) * 100, 1)

    if risk_score >= PHISHING_THRESHOLD:
        verdict = "Phishing"
    elif risk_score >= SUSPICIOUS_THRESHOLD:
        verdict = "Suspicious"
    else:
        verdict = "Legitimate"

    return {
        "verdict": verdict,
        "risk_score": risk_score,
        "reasons": get_reasons(features),
    }


def main():
    model = load_model()

    while True:
        url = input("\nEnter a URL (press Enter to quit): ").strip()
        if not url:
            break

        try:
            result = analyze_url(model, url)
        except InvalidURLError as error:
            print(error)
            continue

        print(f"Verdict: {result['verdict']}")
        print(f"Risk score: {result['risk_score']}%")

        if result["reasons"]:
            print("Warning signs:")
            for reason in result["reasons"]:
                print(f"  - {reason}")
        elif result["verdict"] == "Phishing":
            print("The model flagged this URL from a combination of features.")
        elif result["verdict"] == "Suspicious":
            print("The model is not sure about this URL. Be careful with it.")
        else:
            print("No obvious warning signs were found in the URL.")

        print("Note: only the domain part of the URL is analyzed.")
        print("Note: this is an estimate, not a guarantee of safety.")


if __name__ == "__main__":
    main()
