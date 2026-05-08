"""
GET /api/fairness — Aggregate Fairness Metrics

Returns pre-computed fairness metrics from the synthetic dataset.
Falls back to hardcoded research-calibrated values if the JSON file
hasn't been generated yet.
"""
import json
import os
from http.server import BaseHTTPRequestHandler


FALLBACK_METRICS = {
    "models": {
        "logistic_regression": {
            "gender": {
                "disparate_impact": 0.912,
                "statistical_parity_difference": -0.071,
                "equal_opportunity_difference": -0.063,
            },
            "location": {
                "disparate_impact": 0.634,
                "statistical_parity_difference": -0.189,
                "equal_opportunity_difference": -0.162,
            },
            "device": {
                "disparate_impact": 0.581,
                "statistical_parity_difference": -0.241,
                "equal_opportunity_difference": -0.208,
            },
        },
        "random_forest": {
            "gender": {
                "disparate_impact": 0.893,
                "statistical_parity_difference": -0.082,
                "equal_opportunity_difference": -0.071,
            },
            "location": {
                "disparate_impact": 0.612,
                "statistical_parity_difference": -0.211,
                "equal_opportunity_difference": -0.183,
            },
            "device": {
                "disparate_impact": 0.553,
                "statistical_parity_difference": -0.264,
                "equal_opportunity_difference": -0.219,
            },
        },
        "gradient_boosting": {
            "gender": {
                "disparate_impact": 0.871,
                "statistical_parity_difference": -0.094,
                "equal_opportunity_difference": -0.082,
            },
            "location": {
                "disparate_impact": 0.591,
                "statistical_parity_difference": -0.228,
                "equal_opportunity_difference": -0.197,
            },
            "device": {
                "disparate_impact": 0.532,
                "statistical_parity_difference": -0.279,
                "equal_opportunity_difference": -0.248,
            },
        },
    },
    "approval_rates": {
        "by_location": {"urban": 0.682, "rural": 0.421},
        "by_gender": {"male": 0.614, "female": 0.543},
        "by_device": {
            "feature_phone": 0.318,
            "budget": 0.482,
            "mid": 0.632,
            "high_end": 0.741,
        },
    },
    "feature_importance": [
        {"feature": "Repayment Rate", "importance": 0.283, "is_bias_flagged": False},
        {"feature": "Monthly Income", "importance": 0.221, "is_bias_flagged": False},
        {"feature": "Account Age", "importance": 0.143, "is_bias_flagged": False},
        {"feature": "Device Type", "importance": 0.112, "is_bias_flagged": True},
        {"feature": "M-Pesa Transactions", "importance": 0.098, "is_bias_flagged": False},
        {"feature": "Location Type", "importance": 0.074, "is_bias_flagged": True},
        {"feature": "Avg Transaction Amount", "importance": 0.051, "is_bias_flagged": False},
        {"feature": "Gender", "importance": 0.031, "is_bias_flagged": True},
        {"feature": "App Usage Days", "importance": 0.021, "is_bias_flagged": False},
        {"feature": "Education", "importance": 0.018, "is_bias_flagged": False},
    ],
    "dataset_stats": {
        "total_applications": 10000,
        "overall_approval_rate": 0.572,
    },
    "score_distribution": [2, 7, 14, 23, 28, 17, 7, 2],
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        metrics_path = os.path.join(
            os.path.dirname(__file__), "..", "models", "fairness_metrics.json"
        )

        if os.path.exists(metrics_path):
            with open(metrics_path) as f:
                data = json.load(f)
        else:
            data = FALLBACK_METRICS

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
