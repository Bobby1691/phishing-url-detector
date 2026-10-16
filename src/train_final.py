"""Train the final XGBoost model and save it to disk."""

import os

import pandas as pd
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

DATA_PATH = "data/processed/features.csv"
MODEL_PATH = "models/phishing_model.json"

# In this dataset, label 0 means phishing and label 1 means legitimate.
PHISHING_LABEL = 0


def main():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=["label"])
    y = df["label"]

    # Use the same split as in compare_models.py so the scores are comparable.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(n_estimators=100, random_state=42, eval_metric="logloss")
    model.fit(X_train, y_train)

    # Sanity check: these numbers should match the comparison table.
    predictions = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    recall = recall_score(y_test, predictions, pos_label=PHISHING_LABEL)
    print(f"Phishing recall: {recall:.4f}")

    # Save the trained model so the application can load it later.
    os.makedirs("models", exist_ok=True)
    model.save_model(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
