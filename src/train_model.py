"""Train and evaluate a Logistic Regression model on URL features."""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = "data/processed/features.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    # X holds the input features, y holds the correct answers.
    X = df.drop(columns=["label"])
    y = df["label"]

    # Keep 20% of the data aside for testing. The model never sees it while learning.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale the numbers to a similar range, then fit Logistic Regression.
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(X_train, y_train)

    # Evaluate on the unseen test data.
    predictions = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(
        classification_report(
            y_test, predictions, target_names=["phishing (0)", "legitimate (1)"]
        )
    )


if __name__ == "__main__":
    main()
