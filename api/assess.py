"""
POST /api/assess — Credit Assessment Endpoint

Accepts a user's financial profile, runs the credit scoring model,
saves the assessment to Supabase, and returns a full score breakdown.
"""
import json
import os
import math
from http.server import BaseHTTPRequestHandler

import joblib
import numpy as np


# ── Bias parameters (research-calibrated) ───────────────────
GENDER_PENALTY_FEMALE = -3.0
LOCATION_PENALTY_RURAL = -8.0
DEVICE_PENALTIES = {
    "feature_phone": -7.0,
    "budget": -3.5,
    "mid": 0.0,
    "high_end": 2.5,
}

# ── Feature engineering ───────────────────────────────────────
def engineer_features(data: dict) -> np.ndarray:
    """Convert raw profile data into the feature vector expected by the model."""
    income_norm = min(data.get("monthly_income", 0) / 100_000, 1.0)
    tx_norm = min(data.get("mpesa_transactions_monthly", 0) / 150, 1.0)
    avg_tx_norm = min(data.get("avg_transaction_amount", 0) / 50_000, 1.0)
    age_norm = (data.get("age", 30) - 18) / (65 - 18)
    account_age_norm = min(data.get("account_age_months", 0) / 60, 1.0)
    prev_loans_norm = min(data.get("previous_loans", 0) / 10, 1.0)
    repayment = data.get("repayment_rate", 1.0) if data.get("previous_loans", 0) > 0 else 1.0
    app_usage_norm = min(data.get("app_usage_days", 0) / 30, 1.0)
    platform_norm = min(data.get("platform_connections", 1) / 5, 1.0)

    # Encode categorical
    is_urban = 1.0 if data.get("location_type", "Urban") == "Urban" else 0.0
    is_female = 1.0 if data.get("gender", "M") == "F" else 0.0

    device_map = {"feature_phone": 0.0, "budget": 0.33, "mid": 0.67, "high_end": 1.0}
    device_val = device_map.get(data.get("device_type", "mid"), 0.5)

    edu_map = {"Primary": 0.0, "Secondary": 0.2, "Certificate": 0.4,
               "Diploma": 0.6, "Degree": 0.8, "Postgraduate": 1.0}
    edu_val = edu_map.get(data.get("education", "Diploma"), 0.6)

    emp_map = {"Unemployed": 0.0, "Student": 0.2, "Informal/casual work": 0.4,
               "Self-employed": 0.6, "Formal employment": 1.0}
    emp_val = emp_map.get(data.get("employment_status", "Formal employment"), 0.6)

    return np.array([[
        income_norm, tx_norm, avg_tx_norm, age_norm, account_age_norm,
        prev_loans_norm, repayment, app_usage_norm, platform_norm,
        is_urban, is_female, device_val, edu_val, emp_val,
    ]])


def compute_score_breakdown(data: dict, base_score: float) -> dict:
    """
    Decompose the credit score into factor contributions.
    Returns contributions and bias penalties.
    """
    income = data.get("monthly_income", 0)
    income_contribution = min((income / 100_000) * 25, 25)

    repayment_rate = data.get("repayment_rate", 1.0) if data.get("previous_loans", 0) > 0 else 1.0
    repayment_contribution = repayment_rate * 25

    account_age = data.get("account_age_months", 0)
    account_age_contribution = min((account_age / 60) * 15, 15)

    tx = data.get("mpesa_transactions_monthly", 0)
    transaction_contribution = min((tx / 150) * 20, 20)

    # Bias penalties
    location_penalty = LOCATION_PENALTY_RURAL if data.get("location_type") == "Rural" else 0.0
    device_penalty = DEVICE_PENALTIES.get(data.get("device_type", "mid"), 0.0)
    gender_penalty = GENDER_PENALTY_FEMALE if data.get("gender") == "F" else 0.0

    # Score without bias = base_score minus all bias adjustments
    total_bias = location_penalty + device_penalty + gender_penalty
    score_without_bias = min(max(base_score - total_bias, 0), 100)

    return {
        "income_contribution": round(income_contribution, 2),
        "repayment_contribution": round(repayment_contribution, 2),
        "account_age_contribution": round(account_age_contribution, 2),
        "transaction_contribution": round(transaction_contribution, 2),
        "location_penalty": round(location_penalty, 2),
        "device_penalty": round(device_penalty, 2),
        "gender_penalty": round(gender_penalty, 2),
        "score_without_bias": round(score_without_bias, 2),
    }


def get_recommendations(data: dict, breakdown: dict) -> list:
    recs = []
    if breakdown["transaction_contribution"] < 10:
        recs.append("Increase your M-Pesa activity. Aim for 30+ transactions per month to improve your score.")
    if breakdown["repayment_contribution"] < 15:
        if data.get("previous_loans", 0) == 0:
            recs.append("Start with a small loan (KES 500–1,000) and repay immediately to build a positive credit history.")
        else:
            recs.append("Focus on repaying current loans on time — your repayment history is the strongest score factor.")
    if breakdown["account_age_contribution"] < 8:
        recs.append("Continue using the platform consistently. Account age improves automatically over time.")
    if breakdown["income_contribution"] < 10:
        recs.append("Consider documenting informal income through consistent M-Pesa deposits to improve your income signal.")
    if breakdown["location_penalty"] < 0:
        recs.append("Your location attracts a bias penalty. This is unfair — you may cite CBK Digital Credit Guidelines when challenging a loan denial.")
    if not recs:
        recs.append("Your profile looks strong! Keep maintaining your good financial habits.")
    return recs


def compute_approval_probability(credit_score: float) -> float:
    """Sigmoid-based approval probability from credit score."""
    return round(1 / (1 + math.exp(-0.12 * (credit_score - 50))), 3)


def score_to_anon_buckets(data: dict, credit_score: float) -> dict:
    """Convert precise values to privacy-safe buckets for anonymized_data table."""
    age = data.get("age", 30)
    age_group = "18-25" if age <= 25 else "26-35" if age <= 35 else "36-45" if age <= 45 else "46-55" if age <= 55 else "56-65"

    income = data.get("monthly_income", 0)
    income_bracket = "below_20k" if income < 20_000 else "20k-50k" if income < 50_000 else "50k-100k" if income < 100_000 else "above_100k"

    device_map = {"feature_phone": "feature", "budget": "budget", "mid": "mid", "high_end": "high"}
    device_tier = device_map.get(data.get("device_type", "mid"), "mid")

    bias_total = (
        (LOCATION_PENALTY_RURAL if data.get("location_type") == "Rural" else 0) +
        DEVICE_PENALTIES.get(data.get("device_type", "mid"), 0) +
        (GENDER_PENALTY_FEMALE if data.get("gender") == "F" else 0)
    )

    return {
        "age_group": age_group,
        "gender": data.get("gender"),
        "county": data.get("county"),
        "location_type": data.get("location_type"),
        "education": data.get("education"),
        "employment_status": data.get("employment_status"),
        "income_bracket": income_bracket,
        "device_tier": device_tier,
        "credit_score": round(credit_score, 2),
        "approved": credit_score >= 50,
        "bias_total": round(bias_total, 2),
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self._handle_post()
        except Exception as e:
            import traceback
            self._respond(500, {"error": str(e), "trace": traceback.format_exc()})

    def _handle_post(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self._respond(400, {"error": "Invalid JSON body"})
            return

        # Load model (fallback to rule-based if not found)
        model = None
        try:
            model_path = os.path.join(os.path.dirname(__file__), "..", "models", "random_forest.pkl")
            model = joblib.load(model_path)
        except Exception:
            model = None

        # Compute credit score
        if model is not None:
            features = engineer_features(data)
            raw_prob = model.predict_proba(features)[0][1]
            base_score = raw_prob * 100
        else:
            income_norm = min(data.get("monthly_income", 0) / 100_000, 1.0)
            tx_norm = min(data.get("mpesa_transactions_monthly", 0) / 150, 1.0)
            repayment = data.get("repayment_rate", 1.0) if data.get("previous_loans", 0) > 0 else 0.8
            age_norm = (min(max(data.get("age", 30), 18), 65) - 18) / 47
            account_age_norm = min(data.get("account_age_months", 0) / 60, 1.0)
            base_score = (income_norm * 25 + tx_norm * 20 + repayment * 25 +
                          account_age_norm * 15 + age_norm * 5 + 10)

        breakdown = compute_score_breakdown(data, base_score)
        total_bias = breakdown["location_penalty"] + breakdown["device_penalty"] + breakdown["gender_penalty"]
        credit_score = min(max(base_score + total_bias, 0), 100)
        approval_probability = compute_approval_probability(credit_score)

        top_features = [
            {"feature": "repayment_rate", "impact": round(breakdown["repayment_contribution"] / 100, 3), "is_bias_flagged": False},
            {"feature": "monthly_income", "impact": round(breakdown["income_contribution"] / 100, 3), "is_bias_flagged": False},
            {"feature": "account_age_months", "impact": round(breakdown["account_age_contribution"] / 100, 3), "is_bias_flagged": False},
            {"feature": "mpesa_transactions", "impact": round(breakdown["transaction_contribution"] / 100, 3), "is_bias_flagged": False},
            {"feature": "location_type", "impact": round(abs(breakdown["location_penalty"]) / 100, 3), "is_bias_flagged": True},
            {"feature": "device_type", "impact": round(abs(breakdown["device_penalty"]) / 100, 3), "is_bias_flagged": True},
            {"feature": "gender", "impact": round(abs(breakdown["gender_penalty"]) / 100, 3), "is_bias_flagged": True},
        ]

        recommendations = get_recommendations(data, breakdown)
        self._save_to_supabase(data, credit_score, approval_probability, breakdown, top_features)

        self._respond(200, {
            "credit_score": round(credit_score, 2),
            "approval_probability": approval_probability,
            "approved": credit_score >= 50,
            "score_breakdown": breakdown,
            "top_features": top_features,
            "recommendations": recommendations,
        })

    def _save_to_supabase(self, data, credit_score, approval_probability, breakdown, top_features):
        """Save assessment to Supabase using the service key."""
        import urllib.request
        import urllib.error

        supabase_url = os.environ.get("SUPABASE_URL", "")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

        if not supabase_url or not service_key:
            return  # No Supabase config — skip silently in local dev

        user_id = data.get("user_id")
        if not user_id:
            return

        # Insert assessment
        assessment_record = {
            "user_id": user_id,
            "credit_score": round(credit_score, 2),
            "approval_probability": approval_probability,
            "approved": credit_score >= 50,
            "income_contribution": breakdown["income_contribution"],
            "repayment_contribution": breakdown["repayment_contribution"],
            "account_age_contribution": breakdown["account_age_contribution"],
            "transaction_contribution": breakdown["transaction_contribution"],
            "location_penalty": breakdown["location_penalty"],
            "device_penalty": breakdown["device_penalty"],
            "gender_penalty": breakdown["gender_penalty"],
            "score_without_bias": breakdown["score_without_bias"],
            "model_used": "random_forest",
            "top_features": top_features,
        }

        try:
            req = urllib.request.Request(
                f"{supabase_url}/rest/v1/assessments",
                data=json.dumps(assessment_record).encode(),
                headers={
                    "Content-Type": "application/json",
                    "apikey": service_key,
                    "Authorization": f"Bearer {service_key}",
                    "Prefer": "return=minimal",
                },
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # Non-fatal — don't fail the assessment response

        # Anonymized data if consent given
        if data.get("data_anonymized_consent"):
            anon = score_to_anon_buckets(data, credit_score)
            try:
                req = urllib.request.Request(
                    f"{supabase_url}/rest/v1/anonymized_data",
                    data=json.dumps(anon).encode(),
                    headers={
                        "Content-Type": "application/json",
                        "apikey": service_key,
                        "Authorization": f"Bearer {service_key}",
                        "Prefer": "return=minimal",
                    },
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass

    def _respond(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
