"""Compare Logistic Regression, Random Forest and XGBoost on URL features."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

DATA_PATH = "data/processed/features.csv"

# In this dataset, label 0 means phishing and label 1 means legitimate.
PHISHING_LABEL = 0


def main():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=["label"])
    y = df["label"]

    # Use the same split for every model so the comparison is fair.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000)
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, random_state=42, eval_metric="logloss"
        ),
    }

    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        # Precision, recall and F1 are measured for the phishing class.
        results.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, predictions),
                "precision": precision_score(
                    y_test, predictions, pos_label=PHISHING_LABEL
                ),
                "recall": recall_score(y_test, predictions, pos_label=PHISHING_LABEL),
                "f1": f1_score(y_test, predictions, pos_label=PHISHING_LABEL),
            }
        )

    print(pd.DataFrame(results).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
