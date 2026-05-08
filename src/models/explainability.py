"""
src/models/explainability.py
============================
SHAP analysis on the Random Forest model.
Generates feature importance JSON for the research dashboard.

Run: python src/models/explainability.py
Prerequisites: src/models/train.py must have run first.
Output: models/shap_feature_importance.json
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from train import encode_features, FEATURE_COLS, LABEL_COL

FEATURE_LABELS = [
    ("Age", False),
    ("Monthly Income", False),
    ("M-Pesa Transactions", False),
    ("Avg Transaction Amount", False),
    ("Account Age (months)", False),
    ("Previous Loans", False),
    ("Repayment Rate", False),
    ("App Usage Days", False),
    ("Platform Connections", False),
    ("Location Type", True),    # BIAS
    ("Gender", True),           # BIAS
    ("Device Type", True),      # BIAS
    ("Education Level", False),
    ("Employment Status", False),
]


def run_shap_analysis(sample_size: int = 1000):
    try:
        import shap
    except ImportError:
        print("shap not installed. Run: pip install shap")
        print("Falling back to permutation importance...")
        return run_permutation_importance()

    dataset_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "synthetic_dataset.csv"
    )
    df = pd.read_csv(dataset_path)
    df = encode_features(df)
    X = df[FEATURE_COLS].values
    y = df[LABEL_COL].astype(int).values

    # Sample for speed
    rng = np.random.default_rng(42)
    idx = rng.choice(len(X), size=min(sample_size, len(X)), replace=False)
    X_sample = X[idx]

    model_path = os.path.join("models", "random_forest.pkl")
    model = joblib.load(model_path)

    print(f"Running SHAP on {len(X_sample)} samples...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # For binary classification, shap_values is a list [class0, class1]
    if isinstance(shap_values, list):
        vals = shap_values[1]  # positive class
    else:
        vals = shap_values

    mean_abs_shap = np.abs(vals).mean(axis=0)
    total = mean_abs_shap.sum()

    result = []
    for i, (label, is_bias) in enumerate(FEATURE_LABELS):
        if i < len(mean_abs_shap):
            result.append({
                "feature": label,
                "importance": round(float(mean_abs_shap[i] / total), 4),
                "mean_abs_shap": round(float(mean_abs_shap[i]), 4),
                "is_bias_flagged": is_bias,
            })

    result.sort(key=lambda x: -x["importance"])
    return result


def run_permutation_importance():
    """Fallback when SHAP is not available — uses built-in RF feature importances."""
    model_path = os.path.join("models", "random_forest.pkl")
    model = joblib.load(model_path)
    rf = model.named_steps["clf"] if hasattr(model, "named_steps") else model
    importances = rf.feature_importances_
    total = importances.sum()

    result = []
    for i, (label, is_bias) in enumerate(FEATURE_LABELS):
        if i < len(importances):
            result.append({
                "feature": label,
                "importance": round(float(importances[i] / total), 4),
                "is_bias_flagged": is_bias,
            })

    result.sort(key=lambda x: -x["importance"])
    return result


if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)

    print("Running explainability analysis...")
    try:
        features = run_shap_analysis()
        method = "SHAP"
    except Exception as e:
        print(f"SHAP failed ({e}), using permutation importance")
        features = run_permutation_importance()
        method = "permutation_importance"

    output = {
        "method": method,
        "model": "random_forest",
        "features": features,
    }

    out_path = os.path.join("models", "shap_feature_importance.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nTop features ({method}):")
    for f in features[:8]:
        bias_tag = " ⚠ BIAS" if f["is_bias_flagged"] else ""
        print(f"  {f['feature']:30s} {f['importance']:.3f}{bias_tag}")

    print(f"\nSaved to {out_path}")
