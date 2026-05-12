# Digital Credit Scoring Bias Audit - Implementation Guide

## Project Overview
**Title:** Auditing Algorithmic Bias in Digital Credit Scoring Using Alternative Financial Data: A Simulation-Based Analysis

**Student:** Alexander Wambugu 
**Registration Number:** SCT213-C002-0002/2022  
**Institution:** JOMO KENYATTA UNIVERSITY OF AGRICULTURE AND TECHNOLOGY  
**Program:** Bachelor of Science in Data Science and Analytics

---

## Project Structure

```
credit-bias-audit/
│
├── data/
│   ├── raw/
│   │   └── synthetic_credit_data.csv
│   ├── processed/
│   │   └── processed_features.csv
│   └── results/
│       └── model_predictions.csv
│
├── notebooks/
│   ├── 01_data_generation.ipynb
│   ├── 02_eda_bias_detection.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_explainability_analysis.ipynb
│   └── 05_results_visualization.ipynb
│
├── src/
│   ├── __init__.py
│   ├── phase1_data_generation.py
│   ├── phase2_eda_bias.py
│   ├── phase3_models.py
│   ├── phase4_explainability.py
│   └── utils.py
│
├── models/
│   ├── logistic_regression_model.pkl
│   ├── random_forest_model.pkl
│   └── gradient_boosting_model.pkl
│
├── visualizations/
│   ├── bias_analysis_visualizations.png
│   ├── fairness_comparison.png
│   ├── shap_summary_beeswarm.png
│   ├── shap_summary_bar.png
│   └── feature_importance_comparison.png
│
├── dashboard/
│   ├── app.py (Streamlit/React dashboard)
│   └── requirements.txt
│
├── reports/
│   ├── proposal.docx
│   ├── final_report.pdf
│   └── presentation.pptx
│
├── master_pipeline.py
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager
- 8GB RAM minimum (16GB recommended for SHAP analysis)

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install pandas numpy scikit-learn matplotlib seaborn
pip install shap scipy jupyter
pip install streamlit plotly  # For dashboard

# Alternative: Install from requirements file
pip install -r requirements.txt
```

### 3. Requirements.txt Content
```txt
pandas>=1.5.0
numpy>=1.23.0
scikit-learn>=1.2.0
matplotlib>=3.6.0
seaborn>=0.12.0
shap>=0.41.0
scipy>=1.9.0
jupyter>=1.0.0
streamlit>=1.20.0
plotly>=5.13.0
```

---

## Running the Analysis

### Option 1: Run Complete Pipeline (Recommended)
```bash
python master_pipeline.py
```

This executes all phases sequentially and generates all outputs.

### Option 2: Run Individual Phases

#### Phase 1: Generate Synthetic Data
```bash
python src/phase1_data_generation.py
```
**Output:** `synthetic_credit_data.csv` (15,000 records)

#### Phase 2: Exploratory Analysis & Bias Detection
```bash
python src/phase2_eda_bias.py
```
**Outputs:**
- `bias_analysis_visualizations.png`
- Statistical test results in console
- Disparate impact calculations

#### Phase 3: Train ML Models & Evaluate Fairness
```bash
python src/phase3_models.py
```
**Outputs:**
- Trained models (`.pkl` files)
- `fairness_comparison.png`
- Model performance metrics

#### Phase 4: Explainability Analysis
```bash
python src/phase4_explainability.py
```
**Outputs:**
- `shap_summary_beeswarm.png`
- `shap_summary_bar.png`
- Feature importance charts

### Option 3: Interactive Jupyter Notebooks
```bash
jupyter notebook
# Then open notebooks in order: 01, 02, 03, 04, 05
```

---

## Dashboard Usage

### Streamlit Dashboard (Python)
```bash
cd dashboard
streamlit run app.py
```
Access at: `http://localhost:8501`

### React Dashboard
The React dashboard artifact can be accessed directly through Claude's interface for demonstration.

---

## Key Features Implemented

### ✅ Phase 1: Data Generation
- Synthetic dataset with 15,000 credit applications
- Realistic Kenyan fintech context (M-Pesa, counties, etc.)
- Intentional bias injection for analysis
- 20+ features including demographic, financial, and behavioral data

### ✅ Phase 2: Bias Detection
- Demographic bias analysis (gender, location, county)
- Disparate impact ratio calculations (80% rule)
- Statistical significance testing (Chi-square, t-tests)
- Cramér's V effect size computation
- Comprehensive visualizations

### ✅ Phase 3: Machine Learning
- Three classification models:
  - Logistic Regression (baseline)
  - Random Forest (tree-based)
  - Gradient Boosting (ensemble)
- Standard ML metrics (accuracy, precision, recall, F1, ROC-AUC)
- Fairness metrics:
  - Disparate Impact
  - Statistical Parity Difference
  - Equal Opportunity Difference
  - False Positive Rate parity

### ✅ Phase 4: Explainability
- SHAP (SHapley Additive exPlanations) analysis
- Feature importance rankings
- Individual prediction explanations (waterfall plots)
- Protected group SHAP value comparisons
- Permutation importance

### ✅ Phase 5: Dashboard
- Interactive credit score simulator
- Real-time bias impact calculator
- Feature importance visualizations
- Fairness metrics monitoring
- Protected group comparisons

---

## Key Findings (Expected)

### Bias Detection Results
1. **Location Bias** (High Severity)
   - Rural: 52% approval | Urban: 68% approval
   - Disparate Impact Ratio: **0.76** (FAILS 80% rule)
   - Credit score penalty: **-8 points** for rural applicants

2. **Device Type Bias** (Medium Severity)
   - Feature phone: 42% | High-end: 73% approval
   - Acts as proxy for socioeconomic status

3. **Gender Bias** (Low Severity)
   - Female: 58% | Male: 63% approval
   - Disparate Impact: **0.92** (PASSES 80% rule)

### Model Performance
- **Random Forest:** 78.6% accuracy, best fairness-performance balance
- **Gradient Boosting:** 79.2% accuracy, slightly worse fairness
- **Logistic Regression:** 72.3% accuracy, most interpretable

### Feature Importance
1. Monthly Income (25%)
2. Repayment Rate (22%)
3. Account Age (15%)
4. **Location Type (12%)** ⚠️ Protected attribute
5. M-Pesa Transactions (10%)

---

## For Your Project Proposal

### Chapter 1: Introduction

**Problem Statement:**
"Digital lending platforms in Kenya and across Africa increasingly rely on alternative data (mobile money transactions, device characteristics, location data) for credit scoring. While this expands financial inclusion, concerns exist about algorithmic bias systematically disadvantaging rural populations, women, and lower socioeconomic groups through proxy discrimination."

**Research Objectives:**
1. Simulate a realistic digital credit scoring system using synthetic alternative financial data
2. Quantify algorithmic bias across demographic groups using fairness metrics
3. Train and evaluate multiple ML classification models for credit approval prediction
4. Apply explainable AI techniques to identify bias-contributing features
5. Develop an interactive dashboard for bias transparency and simulation

**Research Questions:**
1. Do commonly used alternative data features exhibit disparate impact across protected groups?
2. Which features contribute most to biased credit outcomes?
3. Can fairness-aware model evaluation identify systematic discrimination?
4. How do different ML algorithms compare in terms of fairness-performance tradeoffs?

### Chapter 2: Literature Review

**Key Topics to Cover:**
- Algorithmic fairness in credit scoring (Barocas & Selbst, 2016)
- Disparate impact in machine learning (Feldman et al., 2015)
- Alternative data in financial services (Berg et al., 2020)
- Fairness metrics and evaluation (Mehrabi et al., 2021)
- Explainable AI in credit decisions (GDPR Article 22)

### Chapter 3: Methodology

**Data:**
- Source: Synthetic generation based on Kenyan fintech patterns
- Size: 15,000 applications
- Features: 20+ (demographic, financial, behavioral)
- Target: Binary loan approval

**Models:**
- Logistic Regression (interpretable baseline)
- Random Forest (non-linear relationships)
- Gradient Boosting (state-of-the-art performance)

**Evaluation:**
- Performance: Accuracy, Precision, Recall, F1, ROC-AUC
- Fairness: Disparate Impact, Statistical Parity, Equal Opportunity
- Explainability: SHAP values, feature importance

**Tools:**
- Python 3.8+
- scikit-learn (modeling)
- SHAP (explainability)
- Pandas/NumPy (data processing)
- Matplotlib/Seaborn (visualization)

### Chapter 4: Budget & Schedule

**Budget:**
```
Item                              Cost (KES)
Internet (6 months @ 2000/month)      12,000
Computing resources (Colab Pro)        2,500
Printing & binding                     3,000
Documentation software                 1,000
TOTAL                                 18,500
```

**Gantt Chart Phases:**
- Weeks 1-2: Proposal & literature review
- Weeks 3-4: Data generation & EDA
- Weeks 5-7: Model development & training
- Week 8: Explainability analysis
- Week 9: Dashboard development
- Weeks 10-11: Report writing
- Week 12: Final presentation prep

---

## Tips for Your Implementation

### 1. **Start Simple, Then Expand**
   - Run Phase 1 first, verify data looks realistic
   - Check visualizations in Phase 2 before proceeding
   - Train one model at a time

### 2. **Document Everything**
   - Keep a research journal
   - Screenshot all visualizations
   - Note unexpected findings

### 3. **Focus on Interpretation**
   - Don't just report numbers
   - Explain what bias metrics mean
   - Discuss real-world implications

### 4. **Be Honest About Limitations**
   - Synthetic data limitations
   - Simplified bias modeling
   - Scope constraints

### 5. **Prepare for Questions**
   - Why these specific biases?
   - How realistic is the synthetic data?
   - What are mitigation strategies?
   - Ethical considerations?

---

## Common Issues & Solutions

### Issue: SHAP takes too long
**Solution:** Reduce sample size in `shap_analysis(sample_size=100)`

### Issue: Memory error with large dataset
**Solution:** Process in batches or reduce to 10,000 samples

### Issue: Fairness metrics seem confusing
**Solution:** Focus on Disparate Impact first (easiest to interpret)

### Issue: Visualizations unclear
**Solution:** Increase figure size, adjust font sizes, use colorblind-friendly palettes

---

## Evaluation Criteria (What Lecturers Look For)

✅ **Technical Competence** (40%)
- Correct implementation of ML algorithms
- Proper use of fairness metrics
- Valid statistical testing

✅ **Analysis Quality** (30%)
- Meaningful insights from data
- Clear interpretation of results
- Critical thinking about bias

✅ **Documentation** (20%)
- Well-structured report
- Clear methodology
- Proper citations (APA format)

✅ **Innovation** (10%)
- Interactive dashboard
- Explainability analysis
- Real-world relevance

---

## Resources & References

### Academic Papers
- Barocas, S., & Selbst, A. D. (2016). Big data's disparate impact. *California Law Review*.
- Mehrabi, N., et al. (2021). A survey on bias and fairness in machine learning. *ACM Computing Surveys*.
- Feldman, M., et al. (2015). Certifying and removing disparate impact. *KDD*.

### Technical Documentation
- scikit-learn fairness metrics: https://scikit-learn.org/
- SHAP documentation: https://shap.readthedocs.io/
- Fairlearn toolkit: https://fairlearn.org/

### Kenyan Context
- Central Bank of Kenya Digital Credit Guidelines
- Kenya National Bureau of Statistics data
- Financial Sector Deepening (FSD) Kenya reports

---

## Contact & Support

For questions about this implementation:
1. Review the code comments
2. Check the README
3. Consult with your supervisor
4. Reference academic papers

**Good luck with your project! 🚀**

---

*Last Updated: January 2025*
*Version: 1.0*
