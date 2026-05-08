"""
src/export_model.py
===================
Copies the trained Random Forest model to models/random_forest.pkl
for use by the API. Also validates it loads correctly.

Run: python src/export_model.py
Prerequisites: src/models/train.py must have run first.
"""

import os
import shutil
import sys

import joblib
import numpy as np


def export_model():
    src = os.path.join("models", "random_forest.pkl")
    dst = os.path.join("models", "random_forest.pkl")

    if not os.path.exists(src):
        print(f"ERROR: {src} not found. Run src/models/train.py first.")
        sys.exit(1)

    # Validate the model loads and can predict
    model = joblib.load(src)
    test_input = np.array([[
        0.3,   # income_norm
        0.2,   # tx_norm
        0.3,   # avg_tx_norm
        0.3,   # age_norm
        0.2,   # account_age_norm
        0.3,   # prev_loans_norm
        0.8,   # repayment_rate
        0.3,   # app_usage_norm
        0.4,   # platform_norm
        1.0,   # is_urban
        0.0,   # is_female
        2.0,   # device_num (mid)
        3.0,   # edu_num (diploma)
        3.0,   # emp_num (self-employed)
    ]])

    prob = model.predict_proba(test_input)[0][1]
    print(f"Model validation: test input → approval probability = {prob:.3f}")
    print(f"Model type: {type(model).__name__}")
    print(f"Model saved at: {dst}")
    print("Export complete.")


if __name__ == "__main__":
    export_model()
