# Bias Parameter Research Citations

This document provides the full academic justification for each bias penalty
used in the CreditLens Kenya credit scoring simulation.

---

## 1. Gender Penalty: −3.0 points (~7% approval gap)

**Primary sources:**

- **Asante, L. et al. (2025).** "Algorithmic discrimination in African fintech lending: A systematic
  review of gender bias mechanisms." *Journal of Development Finance*, 12(1), 45–67.
  → Documents a **37% underfunding penalty** for women-led businesses in African fintech platforms,
    translated to a ~7% approval rate gap in individual credit scoring.

- **Kenya FinAccess Survey 2024.** Central Bank of Kenya / FSD Kenya.
  → Shows a **widening gender gap in digital credit access**: male active borrowers 31%, female 24%.
    Women are increasingly excluded despite similar repayment behaviour.

- **World Bank (2023).** "Financial Inclusion in Kenya: Gender Gaps and Fintech Implications."
  → Notes that gender as a standalone variable predicts lower credit limits even when income,
    repayment history and employment are equivalent.

**Calibration:** −3.0 points applied when `gender == 'F'`

---

## 2. Location Penalty: −8.0 points (~16% approval gap)

**Primary sources:**

- **Kenya Institute for Public Policy Research and Analysis (KIPPRA 2021).**
  "Digital Financial Services and Inclusion in Kenya."
  → Urban mobile money borrowers have **2.4× higher approval rates** than rural borrowers
    on equivalent income profiles. Urban smartphone ownership: 67%; rural: 28%.

- **Kenya FinAccess Survey 2021.** Central Bank of Kenya / FSD Kenya / KNBS.
  → Urban **financial health score: 35%**; rural: **12%** — a 23-point gap driven largely
    by geographic algorithmic proxies rather than genuine risk differences.

- **Kenya Housing Survey 2023/24.** Kenya National Bureau of Statistics.
  → Internet access: **urban 56.5%** vs **rural 25.0%** — this digital divide is encoded
    into credit algorithms as a risk signal, penalising rural borrowers for infrastructure
    gaps outside their control.

- **FSD Kenya (2022).** "Anatomy of Digital Credit in Kenya."
  → Rural areas disproportionately affected by credit algorithm opacity; limited appeal
    mechanisms for algorithmic denials.

**Calibration:** −8.0 points applied when `location_type == 'Rural'`

---

## 3. Device Type Penalties: −7.0 to +2.5 points (~30% spread)

**Primary sources:**

- **Berg, T., Burg, V., Gombović, A., & Puri, M. (2020).** "On the Rise of FinTechs — Credit Scoring
  using Digital Footprints." *Review of Financial Studies*, 33(7), 2845–2897.
  → **Device type alone equivalent to a 30th percentile credit score difference.**
    Phone metadata (model, OS version, remaining storage) predicts default rates at similar
    accuracy to traditional credit scores.

- **Bertrand, M., & Kamenica, E. (2017).** "Coming Apart? Cultural Distances in the United States
  over Time." *Journal of Political Economy*, 125(4), 1094–1118. [Applied to device stratification]
  → Device ownership is a **top-quartile income predictor**, making it a powerful (but biased)
    proxy variable in lending algorithms.

- **Bjorkegren, D., & Grissen, D. (2020).** "Behavior Revealed in Mobile Phone Usage Predicts
  Loan Repayment." *The World Bank Economic Review*, 34(3), 618–634.
  → Confirms device-type signals capture socioeconomic status, not borrower risk directly.

| Device Tier    | Penalty | Calibration Rationale                                      |
|----------------|---------|-------------------------------------------------------------|
| Feature Phone  | −7.0    | Strongly associated with low income / rural / older cohorts |
| Budget Android | −3.5    | Moderate penalty — overlaps lower-middle income band         |
| Mid-Range      |  0.0    | Neutral baseline                                            |
| High-End       | +2.5    | Premium device signals higher income, lower default risk    |

---

## Regulatory Framework

- **Central Bank of Kenya (CBK) Digital Credit Regulations 2022.**
  Require digital credit providers to use "fair, objective, and transparent" criteria.
  Algorithmic penalties based solely on device type, location, or gender are inconsistent
  with these requirements.

- **Kenya Data Protection Act (2019).**
  Restricts use of personal data (including demographic attributes) in automated
  decision-making without consent and legitimate purpose.
