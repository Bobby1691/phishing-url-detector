
"""Analyze a URL with a schema-compatible trained model."""

import pandas as pd
from xgboost import XGBClassifier

from feature_schema import V1_FEATURES
from features import extract_features
from validation import InvalidURLError, validate_url

MODEL_PATH = "models/phishing_model.json"

SUSPICIOUS_THRESHOLD = 40.0
PHISHING_THRESHOLD = 80.0


def validate_model_schema(model):
    """Reject models that do not match the original V1 feature schema."""
    feature_count = getattr(model, "n_features_in_", None)

    if feature_count != len(V1_FEATURES):
        raise RuntimeError(
            "Incompatible model feature count: "
            f"expected {len(V1_FEATURES)}, received {feature_count}."
        )

    try:
        model_feature_names = model.get_booster().feature_names
    except (AttributeError, TypeError) as error:
        raise RuntimeError(
            "Unable to inspect the model's feature schema."
        ) from error

    if model_feature_names is None:
        raise RuntimeError(
            "Model does not contain feature names; schema cannot be verified."
        )

    if tuple(model_feature_names) != V1_FEATURES:
        raise RuntimeError(
            "Incompatible model feature names or ordering. "
            "This prediction pipeline requires the V1 feature schema."
        )


def load_model():
    """Load and validate the V1 model."""
    model = XGBClassifier()
    model.load_model(MODEL_PATH)
    validate_model_schema(model)
    return model


def _phishing_probability(model, features_df):
    """Return the probability associated with class label 0."""
    classes = list(model.classes_)

    try:
        phishing_index = classes.index(0)
    except ValueError as error:
        raise RuntimeError(
            "The model does not contain phishing class label 0."
        ) from error

    probabilities = model.predict_proba(features_df)

    if (
        probabilities.ndim != 2
        or probabilities.shape[0] != 1
        or probabilities.shape[1] != len(classes)
    ):
        raise RuntimeError("The model returned an invalid probability shape.")

    return float(probabilities[0][phishing_index])


def get_reasons(features):
    """Return human-readable warning signs found in URL features."""
    reasons = []

    if features["has_ip_address"] == 1:
        reasons.append(
            "The address uses a raw IP number instead of a domain name."
        )

    if features["has_https"] == 0:
        reasons.append("The connection is not secured with HTTPS.")

    if features["has_suspicious_word"] == 1:
        reasons.append(
            "The domain contains words often seen in phishing links "
            "(such as login or verify)."
        )

    if features["has_at_symbol"] == 1:
        reasons.append(
            "The URL contains an @ symbol, which can hide the real destination."
        )

    if features["domain_length"] > 30:
        reasons.append("The domain name is unusually long.")

    if features["num_hyphens"] >= 3:
        reasons.append("The domain contains many hyphens.")

    if features["num_subdomains"] >= 3:
        reasons.append("The domain has many subdomains.")

    return reasons


def analyze_url(model, url):
    """Return the verdict, risk score and reasons for a single URL."""
    if not isinstance(url, str):
        raise InvalidURLError(
            "Please enter a valid web address, for example https://example.com"
        )

    url = url.strip()
    validate_url(url)
    validate_model_schema(model)

    features = extract_features(url, schema_version="v1")
    X = pd.DataFrame([features], columns=V1_FEATURES)

    phishing_probability = _phishing_probability(model, X)
    risk_score = round(phishing_probability * 100, 1)

    if risk_score >= PHISHING_THRESHOLD:
        verdict = "Phishing"
    elif risk_score >= SUSPICIOUS_THRESHOLD:
        verdict = "Suspicious"
    else:
        verdict = "Unverified"

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
            print(
                "No strong URL-level warning signs were found; "
                "domain reputation has not been verified."
            )

        print("Note: only the original V1 feature set is used by this model.")
        print("Note: this is an estimate, not a guarantee of safety.")


if __name__ == "__main__":
    main()
