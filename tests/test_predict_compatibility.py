
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest

from feature_schema import V1_FEATURES
from predict import (
    _phishing_probability,
    analyze_url,
    validate_model_schema,
)


class FakeBooster:
    def __init__(self, feature_names):
        self.feature_names = feature_names


class FakeModel:
    def __init__(
        self,
        feature_names=None,
        classes=None,
        probabilities=None,
    ):
        self.n_features_in_ = (
            len(feature_names) if feature_names is not None else 10
        )
        self.classes_ = (
            classes if classes is not None else np.array([0, 1])
        )
        self.probabilities = (
            probabilities
            if probabilities is not None
            else np.array([[0.9, 0.1]])
        )
        self.feature_names = (
            list(feature_names)
            if feature_names is not None
            else list(V1_FEATURES)
        )

    def get_booster(self):
        return FakeBooster(self.feature_names)

    def predict_proba(self, features):
        return self.probabilities


def test_v1_model_schema_is_accepted():
    model = FakeModel(feature_names=V1_FEATURES)
    validate_model_schema(model)


def test_wrong_feature_count_is_rejected():
    model = FakeModel()
    model.n_features_in_ = 25

    with pytest.raises(RuntimeError, match="feature count"):
        validate_model_schema(model)


def test_wrong_feature_order_is_rejected():
    incorrect_order = list(V1_FEATURES)
    incorrect_order[0], incorrect_order[1] = (
        incorrect_order[1],
        incorrect_order[0],
    )

    model = FakeModel(feature_names=incorrect_order)

    with pytest.raises(RuntimeError, match="feature names or ordering"):
        validate_model_schema(model)


def test_missing_feature_names_are_rejected():
    model = FakeModel()
    model.feature_names = None

    with pytest.raises(RuntimeError, match="does not contain feature names"):
        validate_model_schema(model)


def test_phishing_probability_uses_class_label_zero():
    # Deliberately reverse the class order.
    model = FakeModel(
        classes=np.array([1, 0]),
        probabilities=np.array([[0.2, 0.8]]),
    )

    probability = _phishing_probability(model, None)

    assert probability == pytest.approx(0.8)


def test_missing_phishing_class_is_rejected():
    model = FakeModel(
        classes=np.array([1, 2]),
        probabilities=np.array([[0.5, 0.5]]),
    )

    with pytest.raises(RuntimeError, match="phishing class label 0"):
        _phishing_probability(model, None)


def test_analyze_url_preserves_response_contract():
    model = FakeModel(
        classes=np.array([0, 1]),
        probabilities=np.array([[0.9, 0.1]]),
    )

    result = analyze_url(model, "https://example.com")

    assert set(result) == {"verdict", "risk_score", "reasons"}
    assert result["verdict"] == "Phishing"
    assert result["risk_score"] == 90.0
    assert isinstance(result["reasons"], list)
