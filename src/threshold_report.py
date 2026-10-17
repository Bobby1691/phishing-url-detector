"""Show how the decision threshold changes precision and recall."""

import pandas as pd
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

DATA_PATH = "data/processed/features.csv"
MODEL_PATH = "models/phishing_model.json"

# In this dataset, label 0 means phishing and label 1 means legitimate.
THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def main():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=["label"])
    y = df["label"]

    # Use the same split as training so that the test data is unseen by the model.
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier()
    model.load_model(MODEL_PATH)

    # Probability that each test URL is phishing (column 0 is label 0).
    phishing_probability = model.predict_proba(X_test)[:, 0]
    is_phishing = (y_test == 0).to_numpy()

    rows = []
    for threshold in THRESHOLDS:
        flagged = phishing_probability >= threshold
        rows.append(
            {
                "threshold": threshold,
                "precision": precision_score(is_phishing, flagged),
                "recall": recall_score(is_phishing, flagged),
                "false_alarms": int((flagged & ~is_phishing).sum()),
                "missed_phishing": int((~flagged & is_phishing).sum()),
            }
        )

    print(pd.DataFrame(rows).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
