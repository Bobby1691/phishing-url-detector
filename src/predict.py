"""Analyze a URL with the trained model and explain the result."""

import pandas as pd
from xgboost import XGBClassifier

from features import extract_features

MODEL_PATH = "models/phishing_model.json"

# Risk score (in percent) at or above which a URL is reported as phishing.
PHISHING_THRESHOLD = 50.0


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
            "The URL contains words often seen in phishing links (such as login or verify)."
        )
    if features["url_length"] > 75:
        reasons.append("The URL is unusually long.")
    if features["special_chars"] > 12:
        reasons.append("The URL contains many special characters.")
    if features["num_subdomains"] >= 3:
        reasons.append("The URL has many subdomains.")
    return reasons


def analyze_url(model, url):
    """Return the verdict, risk score and reasons for a single URL."""
    features = extract_features(url)
    X = pd.DataFrame([features])

    # Column 0 of predict_proba is label 0 (phishing), column 1 is label 1 (legitimate).
    phishing_probability = model.predict_proba(X)[0][0]
    risk_score = round(float(phishing_probability) * 100, 1)

    verdict = "Phishing" if risk_score >= PHISHING_THRESHOLD else "Legitimate"
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

        result = analyze_url(model, url)
        print(f"Verdict: {result['verdict']}")
        print(f"Risk score: {result['risk_score']}%")

        if result["reasons"]:
            print("Warning signs:")
            for reason in result["reasons"]:
                print(f"  - {reason}")
        elif result["verdict"] == "Phishing":
            print("The model flagged this URL from a combination of features.")
        else:
            print("No obvious warning signs were found in the URL.")

        print("Note: this is an estimate, not a guarantee of safety.")


if __name__ == "__main__":
    main()
