
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import pytest

from build_dataset import build_feature_dataframe
from feature_schema import V1_FEATURES, V2_FEATURES


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "URL": [
            "https://example.com",
            "https://paypal-security-example.com/login",
        ],
        "label": [1, 0],
    })


def test_dataset_builder_defaults_to_v1(sample_dataframe):
    result = build_feature_dataframe(sample_dataframe)

    assert list(result.columns) == [*V1_FEATURES, "label"]
    assert len(result) == 2


def test_dataset_builder_supports_v2(sample_dataframe):
    result = build_feature_dataframe(
        sample_dataframe,
        schema_version="v2",
    )

    assert list(result.columns) == [*V2_FEATURES, "label"]
    assert len(result) == 2


def test_v2_dataset_contains_expected_brand_indicator(sample_dataframe):
    result = build_feature_dataframe(
        sample_dataframe,
        schema_version="v2",
    )

    assert result.iloc[1]["has_brand_impersonation"] == 1


def test_dataset_builder_rejects_missing_columns():
    df = pd.DataFrame({"URL": ["https://example.com"]})

    with pytest.raises(ValueError, match="missing required columns"):
        build_feature_dataframe(df)


@pytest.mark.parametrize("bad_url", [None, "", "   ", 123])
def test_dataset_builder_rejects_invalid_url_values(
    sample_dataframe,
    bad_url,
):
    # Use object dtype so Pandas allows non-string test values.
    sample_dataframe["URL"] = sample_dataframe["URL"].astype(object)
    sample_dataframe.at[0, "URL"] = bad_url

    with pytest.raises(ValueError, match="Invalid or missing URL"):
        build_feature_dataframe(sample_dataframe)


def test_dataset_builder_rejects_missing_label(sample_dataframe):
    sample_dataframe.loc[0, "label"] = None

    with pytest.raises(ValueError, match="Missing label"):
        build_feature_dataframe(sample_dataframe)


def test_dataset_builder_rejects_non_binary_label(sample_dataframe):
    sample_dataframe.loc[0, "label"] = 2

    with pytest.raises(ValueError, match="Invalid label"):
        build_feature_dataframe(sample_dataframe)


def test_dataset_builder_rejects_unsupported_schema(sample_dataframe):
    with pytest.raises(ValueError, match="Unsupported feature schema"):
        build_feature_dataframe(
            sample_dataframe,
            schema_version="v3",
        )
