"""Build a feature table from the PhiUSIIL dataset using only URL-based features."""

import glob
import os

import pandas as pd

from features import extract_features


def main():
    # The raw dataset is expected to be the only CSV file directly inside data/.
    csv_files = glob.glob("data/*.csv")
    if len(csv_files) != 1:
        raise SystemExit(f"Expected exactly one CSV file in data/, found {len(csv_files)}.")

    # Load only the two columns we need.
    df = pd.read_csv(csv_files[0], usecols=["URL", "label"])
    print(f"Loaded {len(df)} rows from {csv_files[0]}")

    # Extract features from every URL.
    rows = [extract_features(url) for url in df["URL"]]
    features_df = pd.DataFrame(rows)
    features_df["label"] = df["label"].values

    # Save the result in a separate folder so the raw data stays untouched.
    os.makedirs("data/processed", exist_ok=True)
    output_path = "data/processed/features.csv"
    features_df.to_csv(output_path, index=False)

    print(f"Saved {features_df.shape[0]} rows and {features_df.shape[1]} columns to {output_path}")
    print(features_df["label"].value_counts())


if __name__ == "__main__":
    main()
