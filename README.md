# CreditLens Kenya

**Know your credit score. See the bias behind it.**

> **Auditing Algorithmic Bias in Digital Credit Scoring Using Alternative Financial Data: A Simulation-Based Analysis**
> Alexander Wambugu · SCT213-C0002-0002/2022 · BSc Data Science & Analytics
> Jomo Kenyatta University of Agriculture and Technology (JKUAT) · 2022–2026

CreditLens is the research deliverable and public-facing tool for this JKUAT Data Science thesis. Enter your financial profile and get a personalised credit score estimate, approval likelihood across major digital lenders, and a clear breakdown of which penalties are legitimate risk factors — and which are algorithmic bias.

Live: [creditlenskenya.vercel.app](https://creditlenskenya.vercel.app) &nbsp;·&nbsp; [Research Dashboard](https://creditlenskenya.vercel.app/research.html)

---

## What It Does

**For borrowers**
- Credit score estimate (0–100) modelled on how M-Shwari, Tala, Branch, and KCB M-Pesa actually score applications
- Approval probability and which platforms are likely to say yes
- Side-by-side: your actual score vs your score without algorithmic bias penalties
- Personalised tips based on your specific weak areas

**For researchers & advocates**
- Public bias dashboard showing disparate impact across gender, location, and device type
- Fairness metrics (Disparate Impact, SPD, EOD) across three ML models
- SHAP feature importance highlighting bias-risk variables
- Bias parameters calibrated to published research on Kenyan fintech

---

## The Bias Problem

Digital lenders in Kenya use alternative data — M-Pesa activity, phone model, GPS location — to score borrowers. Research shows these proxies encode systematic disadvantages that have nothing to do with a borrower's ability to repay:

| Bias Factor | Penalty | Source |
|---|---|---|
| Rural location | −8 pts (~16% approval gap) | KIPPRA 2021, FinAccess 2021 |
| Feature phone | −7 pts (~30% spread across tiers) | Berg et al., 2020 (RFS) |
| Female gender | −3 pts (~7% approval gap) | Asante et al., 2025; FinAccess 2024 |

CreditLens makes these penalties visible and quantified, rather than hidden inside a black-box score.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML, CSS, JavaScript |
| Charts | Chart.js (CDN) |
| API | Python serverless functions (Vercel) |
| Auth + Database | Supabase (PostgreSQL + RLS) |
| ML Models | scikit-learn (Random Forest, LR, Gradient Boosting) |
| Deployment | Vercel |

---

## Running Locally

```bash
git clone https://github.com/Rednax3la/algorithmicbias.git
cd algorithmicbias

# Install dependencies
pip install scikit-learn pandas numpy joblib shap

# Generate data and train models
python src/data/generate.py
python src/models/train.py
python src/models/fairness.py
python src/models/explainability.py

# Open the frontend
open frontend/index.html
```

Add your Supabase credentials to `frontend/js/supabase.js` and set `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` in your environment for the API to persist data.

---

## Project Structure

```
├── frontend/           # HTML, CSS, JS — no framework
│   ├── index.html      # Landing page
│   ├── auth.html       # Sign in / Sign up
│   ├── profile.html    # Financial profile form (3 steps)
│   ├── dashboard.html  # Personal credit health report
│   ├── research.html   # Public bias dashboard
│   ├── css/styles.css
│   └── js/             # supabase.js, auth.js, profile.js, dashboard.js, research.js
├── api/                # Vercel Python serverless functions
│   ├── assess.py       # POST: run credit assessment
│   ├── fairness.py     # GET: aggregate bias metrics
│   └── health.py       # GET: health check
├── src/
│   ├── data/generate.py        # Synthetic dataset generation
│   ├── models/train.py         # Train all three models
│   ├── models/fairness.py      # Compute fairness metrics
│   ├── models/explainability.py # SHAP / permutation importance
│   └── export_model.py         # Validate trained model
├── models/             # Serialised .pkl files + metrics JSON
├── supabase/schema.sql # Database schema with RLS policies
└── requirements.txt    # API runtime dependencies
```

---

## Research Background

Bias parameters are calibrated to peer-reviewed research:

- **Asante et al. (2025)** — 37% underfunding penalty for women in African fintech
- **KIPPRA (2021)** — Urban borrowers approved at 2.4× the rate of rural equivalents
- **Berg et al. (2020)** — Device type alone equivalent to a 30th-percentile credit score gap *(Review of Financial Studies)*
- **Kenya FinAccess Survey 2021/2024** — CBK / FSD Kenya
- **Kenya Housing Survey 2023/24** — Internet access: urban 56.5% vs rural 25.0%

Full citations: [`src/data/bias_sources.md`](src/data/bias_sources.md)

Full thesis: *Auditing Algorithmic Bias in Digital Credit Scoring Using Alternative Financial Data: A Simulation-Based Analysis* — JKUAT, School of Computing and Information Technology.

---

## License

MIT — free to use, adapt, and build on.
