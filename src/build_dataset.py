
"""Build a versioned feature table from the phishing URL dataset."""

import argparse
import glob
import json
import os

import pandas as pd

from feature_schema import get_feature_names
from features import extract_features


OUTPUT_FILES = {
    "v1": "data/processed/features.csv",
    "v2": "data/processed/features_v2.csv",
}


def build_feature_dataframe(df: pd.DataFrame, schema_version: str = "v1"):
    """Build a feature dataframe using one explicit feature schema."""
    expected_columns = {"URL", "label"}
    missing_columns = expected_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_columns)}"
        )

    feature_names = get_feature_names(schema_version)
    rows = []

    for position, (_, row) in enumerate(df.iterrows(), start=2):
        url = row["URL"]
        label = row["label"]

        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                f"Invalid or missing URL at CSV row {position}."
            )

        if pd.isna(label):
            raise ValueError(
                f"Missing label at CSV row {position}."
            )

        if label not in (0, 1):
            raise ValueError(
                f"Invalid label at CSV row {position}: expected 0 or 1."
            )

        try:
            features = extract_features(
                url,
                schema_version=schema_version,
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Feature extraction failed at CSV row {position}: {error}"
            ) from error

        if tuple(features.keys()) != feature_names:
            raise RuntimeError(
                f"Feature schema mismatch at CSV row {position}."
            )

        features["label"] = label
        rows.append(features)

    return pd.DataFrame(
        rows,
        columns=[*feature_names, "label"],
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a versioned phishing URL feature dataset."
    )
    parser.add_argument(
        "--schema-version",
        choices=("v1", "v2"),
        default="v1",
        help="Feature schema to generate (default: v1).",
    )
    args = parser.parse_args(argv)

    csv_files = glob.glob("data/*.csv")

    if len(csv_files) != 1:
        raise SystemExit(
            f"Expected exactly one CSV file in data/, found {len(csv_files)}."
        )

    input_path = csv_files[0]

    try:
        df = pd.read_csv(input_path, usecols=["URL", "label"])
    except (ValueError, OSError) as error:
        raise SystemExit(f"Unable to read dataset: {error}") from error

    print(f"Loaded {len(df)} rows from {input_path}")
    print(f"Feature schema: {args.schema_version}")

    try:
        features_df = build_feature_dataframe(
            df,
            schema_version=args.schema_version,
        )
    except (TypeError, ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from error

    output_path = OUTPUT_FILES[args.schema_version]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    features_df.to_csv(output_path, index=False)

    metadata_path = output_path.removesuffix(".csv") + ".metadata.json"
    metadata = {
        "schema_version": args.schema_version,
        "feature_names": list(get_feature_names(args.schema_version)),
        "label_column": "label",
        "row_count": len(features_df),
        "source_file": input_path,
    }

    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)

    print(
        f"Saved {features_df.shape[0]} rows and "
        f"{features_df.shape[1]} columns to {output_path}"
    )
    print(f"Saved schema metadata to {metadata_path}")
    print(features_df["label"].value_counts())


if __name__ == "__main__":
    main()
