"""
src/data/generate.py
====================
Research-calibrated synthetic data generation for digital credit scoring bias audit.

Run: python src/data/generate.py
Output: data/synthetic_dataset.csv

Bias parameters are calibrated to published research:
  - Gender: Asante et al. (2025), FinAccess 2024
  - Location: KIPPRA 2021, FinAccess 2021, Kenya Housing Survey 2023/24
  - Device: Berg et al. (2020, Review of Financial Studies), Bertrand & Kamenica (2017)
"""

import os
import numpy as np
import pandas as pd
from dataclasses import dataclass

np.random.seed(42)


@dataclass
class BiasParameters:
    # Gender: -3.0 pts → ~7% approval gap
    # Source: Asante et al. (2025) 37% underfunding penalty in African fintech;
    #         FinAccess 2024: widening digital credit gender gap in Kenya
    gender_penalty_female: float = -3.0

    # Location: -8.0 pts → ~16% approval gap
    # Source: KIPPRA 2021 (urban smartphone 2.4x rural);
    #         FinAccess 2021 (urban financial health 35% vs rural 12%);
    #         Kenya Housing Survey 2023/24 (internet: urban 56.5% vs rural 25%)
    location_penalty_rural: float = -8.0

    # Device: tiered penalties → ~30% approval spread across tiers
    # Source: Berg et al. (2020, Review of Financial Studies): device type equivalent
    #         to 30th percentile credit score difference;
    #         Bertrand & Kamenica (2017): device = top-quartile income predictor
    device_penalty_feature_phone: float = -7.0
    device_penalty_budget: float = -3.5
    device_penalty_mid: float = 0.0
    device_penalty_high_end: float = 2.5


COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Machakos", "Kakamega", "Nyeri", "Meru", "Kitale",
    "Garissa", "Marsabit", "Turkana", "Mandera",
]
URBAN_COUNTIES = {"Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"}

EDUCATION_LEVELS = ["Primary", "Secondary", "Certificate", "Diploma", "Degree", "Postgraduate"]
EMPLOYMENT_TYPES = [
    "Formal employment", "Informal/casual work", "Self-employed", "Unemployed", "Student"
]
DEVICE_TYPES = ["feature_phone", "budget", "mid", "high_end"]


def generate_dataset(n_samples: int = 10_000, bias: BiasParameters = None) -> pd.DataFrame:
    if bias is None:
        bias = BiasParameters()

    rng = np.random.default_rng(42)

    # Demographics
    ages = rng.normal(32, 10, n_samples).clip(18, 65).astype(int)
    genders = rng.choice(["M", "F"], n_samples, p=[0.55, 0.45])

    county_probs_raw = [0.25] + [0.08] * 4 + [0.05] * 9
    total = sum(county_probs_raw)
    county_probs = [p / total for p in county_probs_raw]
    counties = rng.choice(COUNTIES, n_samples, p=county_probs)
    location_types = ["Urban" if c in URBAN_COUNTIES else "Rural" for c in counties]

    edu_probs_urban = [0.02, 0.15, 0.15, 0.28, 0.30, 0.10]
    edu_probs_rural = [0.10, 0.35, 0.20, 0.22, 0.10, 0.03]
    educations = [
        rng.choice(EDUCATION_LEVELS, p=edu_probs_urban if lt == "Urban" else edu_probs_rural)
        for lt in location_types
    ]

    emp_probs_urban = [0.35, 0.20, 0.25, 0.10, 0.10]
    emp_probs_rural = [0.15, 0.35, 0.30, 0.12, 0.08]
    employments = [
        rng.choice(EMPLOYMENT_TYPES, p=emp_probs_urban if lt == "Urban" else emp_probs_rural)
        for lt in location_types
    ]

    # Financial features (correlated with location & employment)
    base_income = np.where(
        np.array(location_types) == "Urban",
        rng.lognormal(10.2, 0.7, n_samples),  # ~27k median urban
        rng.lognormal(9.5, 0.7, n_samples),   # ~13k median rural
    ).clip(5_000, 500_000)

    emp_multipliers = {
        "Formal employment": 1.4, "Self-employed": 1.1,
        "Informal/casual work": 0.75, "Student": 0.6, "Unemployed": 0.4
    }
    income_multiplier = np.array([emp_multipliers[e] for e in employments])
    monthly_income = (base_income * income_multiplier).clip(5_000, 500_000)

    mpesa_tx = (rng.normal(35, 20, n_samples) * (monthly_income / 30_000)).clip(1, 150).astype(int)
    avg_tx_amount = (rng.lognormal(7.5, 0.8, n_samples)).clip(100, 50_000)
    account_age = rng.integers(1, 61, n_samples)
    previous_loans = rng.integers(0, 11, n_samples)
    repayment_rate = np.where(
        previous_loans > 0,
        rng.beta(8, 2, n_samples),   # skewed toward high repayment
        1.0
    )
    app_usage_days = rng.integers(0, 31, n_samples)
    platform_connections = rng.integers(1, 6, n_samples)

    # Device (correlated with income & location)
    device_probs = []
    for lt, inc in zip(location_types, monthly_income):
        if lt == "Rural":
            p = [0.25, 0.40, 0.28, 0.07]
        elif inc > 80_000:
            p = [0.02, 0.10, 0.40, 0.48]
        elif inc > 40_000:
            p = [0.05, 0.25, 0.50, 0.20]
        else:
            p = [0.12, 0.45, 0.35, 0.08]
        device_probs.append(p)
    device_types = [rng.choice(DEVICE_TYPES, p=p) for p in device_probs]

    # Compute base credit score (rule-based, 0–100)
    # Use log-scale for income so median earners (25k) get a reasonable contribution
    import numpy as _np
    income_contrib = (_np.log1p(monthly_income) / _np.log1p(500_000) * 25).clip(0, 25)
    repayment_contrib = repayment_rate * 25
    account_contrib = (account_age / 60 * 15).clip(0, 15)
    tx_contrib = (mpesa_tx / 150 * 20).clip(0, 20)
    other_contrib = (app_usage_days / 30 * 5 + platform_connections / 5 * 5 + 5).clip(0, 15)

    base_score = (income_contrib + repayment_contrib + account_contrib + tx_contrib + other_contrib)
    base_score = base_score.clip(0, 100)

    # Apply bias penalties
    location_penalty = np.where(np.array(location_types) == "Rural", bias.location_penalty_rural, 0.0)
    gender_penalty = np.where(genders == "F", bias.gender_penalty_female, 0.0)
    device_penalty_map = {
        "feature_phone": bias.device_penalty_feature_phone,
        "budget": bias.device_penalty_budget,
        "mid": bias.device_penalty_mid,
        "high_end": bias.device_penalty_high_end,
    }
    device_penalty = np.array([device_penalty_map[d] for d in device_types])

    credit_score = (base_score + location_penalty + gender_penalty + device_penalty).clip(0, 100)
    approved = credit_score >= 50.0

    df = pd.DataFrame({
        "age": ages,
        "gender": genders,
        "county": counties,
        "location_type": location_types,
        "education": educations,
        "employment_status": employments,
        "monthly_income": monthly_income.round(0),
        "mpesa_transactions_monthly": mpesa_tx,
        "avg_transaction_amount": avg_tx_amount.round(0),
        "account_age_months": account_age,
        "previous_loans": previous_loans,
        "repayment_rate": repayment_rate.round(3),
        "device_type": device_types,
        "app_usage_days": app_usage_days,
        "platform_connections": platform_connections,
        "credit_score": credit_score.round(2),
        "score_without_bias": base_score.round(2),
        "location_penalty": location_penalty,
        "gender_penalty": gender_penalty,
        "device_penalty": device_penalty,
        "approved": approved,
    })

    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_dataset(n_samples=10_000)
    df.to_csv("data/synthetic_dataset.csv", index=False)
    print(f"Generated {len(df):,} records -> data/synthetic_dataset.csv")
    print(f"Overall approval rate: {df['approved'].mean():.1%}")
    print(f"Urban approval rate:   {df[df.location_type=='Urban']['approved'].mean():.1%}")
    print(f"Rural approval rate:   {df[df.location_type=='Rural']['approved'].mean():.1%}")
    print(f"Male approval rate:    {df[df.gender=='M']['approved'].mean():.1%}")
    print(f"Female approval rate:  {df[df.gender=='F']['approved'].mean():.1%}")
