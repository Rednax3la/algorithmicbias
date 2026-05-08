"""
src/models/train.py
===================
Train Logistic Regression, Random Forest, and Gradient Boosting models
on the synthetic dataset. Saves all three models and evaluation metrics.

Run: python src/models/train.py
Prerequisites: python src/data/generate.py (must have run first)
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


FEATURE_COLS = [
    "age", "monthly_income", "mpesa_transactions_monthly", "avg_transaction_amount",
    "account_age_months", "previous_loans", "repayment_rate", "app_usage_days",
    "platform_connections",
    # Encoded categoricals (added below)
    "is_urban", "is_female", "device_num", "edu_num", "emp_num",
]

LABEL_COL = "approved"

EDU_MAP = {"Primary": 0, "Secondary": 1, "Certificate": 2, "Diploma": 3, "Degree": 4, "Postgraduate": 5}
EMP_MAP = {"Unemployed": 0, "Student": 1, "Informal/casual work": 2, "Self-employed": 3, "Formal employment": 4}
DEVICE_MAP = {"feature_phone": 0, "budget": 1, "mid": 2, "high_end": 3}


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_urban"] = (df["location_type"] == "Urban").astype(int)
    df["is_female"] = (df["gender"] == "F").astype(int)
    df["device_num"] = df["device_type"].map(DEVICE_MAP).fillna(2)
    df["edu_num"] = df["education"].map(EDU_MAP).fillna(3)
    df["emp_num"] = df["employment_status"].map(EMP_MAP).fillna(3)
    return df


def load_data() -> tuple:
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic_dataset.csv")
    if not os.path.exists(dataset_path):
        print("Dataset not found. Running data generation first...")
        import subprocess
        subprocess.run([sys.executable, "src/data/generate.py"], check=True)

    df = pd.read_csv(dataset_path)
    df = encode_features(df)

    X = df[FEATURE_COLS].values
    y = df[LABEL_COL].astype(int).values
    return X, y, df


def train_models(X_train, y_train):
    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, random_state=42, class_weight="balanced")),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, min_samples_leaf=5,
            random_state=42, class_weight="balanced", n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42,
        ),
    }
    fitted = {}
    for name, model in models.items():
        print(f"Training {name}...", end=" ")
        model.fit(X_train, y_train)
        fitted[name] = model
        print("done")
    return fitted


def evaluate_models(models: dict, X_test, y_test) -> dict:
    results = {}
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        results[name] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "report": classification_report(y_test, y_pred, output_dict=True),
        }
        print(f"\n{name}: ACC={results[name]['accuracy']:.3f}, AUC={results[name]['roc_auc']:.3f}")
    return results


def main():
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    X, y, df = load_data()
    print(f"Loaded {len(X):,} records. Positive rate: {y.mean():.1%}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = train_models(X_train, y_train)
    metrics = evaluate_models(models, X_test, y_test)

    # Save all models
    for name, model in models.items():
        path = os.path.join("models", f"{name}.pkl")
        joblib.dump(model, path)
        print(f"Saved {path}")

    # Save evaluation metrics
    with open("models/eval_metrics.json", "w") as f:
        # Remove non-serializable parts
        serializable = {}
        for k, v in metrics.items():
            serializable[k] = {
                "accuracy": v["accuracy"],
                "roc_auc": v["roc_auc"],
            }
        json.dump(serializable, f, indent=2)

    print("\nAll models saved to models/")
    return models, X_test, y_test, df


if __name__ == "__main__":
    main()
