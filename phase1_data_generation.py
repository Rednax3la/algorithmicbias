"""
Phase 1: Synthetic Data Generation for Digital Credit Scoring Bias Audit
=========================================================================
This module generates realistic synthetic data for digital lending simulation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

class DigitalCreditDataGenerator:
    """
    Generates synthetic data mimicking digital lending platforms in Kenya
    Includes demographic, behavioral, and transaction features
    """
    
    def __init__(self, n_samples=10000):
        self.n_samples = n_samples
        self.counties = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 
                         'Machakos', 'Kakamega', 'Nyeri', 'Meru', 'Kitale',
                         'Garissa', 'Marsabit', 'Turkana', 'Mandera']
        self.urban_counties = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
        
    def generate_demographics(self):
        """Generate demographic features"""
        data = {}
        
        # Age distribution (18-65)
        data['age'] = np.random.normal(32, 10, self.n_samples).clip(18, 65).astype(int)
        
        # Gender (slight male skew in digital lending)
        data['gender'] = np.random.choice(['M', 'F'], self.n_samples, p=[0.55, 0.45])
        
        # County distribution (urban bias)
        county_probs = [0.25] + [0.08] * 4 + [0.05] * 9  # Urban counties get higher probability
        data['county'] = np.random.choice(self.counties, self.n_samples, p=county_probs)
        
        # Location type
        data['location_type'] = ['Urban' if c in self.urban_counties else 'Rural' 
                                 for c in data['county']]
        
        # Education level
        education_levels = ['Primary', 'Secondary', 'Certificate', 'Diploma', 'Degree', 'Postgraduate']
        # Urban areas have higher education levels
        data['education'] = [
            np.random.choice(education_levels, p=[0.05, 0.15, 0.25, 0.30, 0.20, 0.05])
            if loc == 'Urban' else
            np.random.choice(education_levels, p=[0.15, 0.30, 0.25, 0.20, 0.08, 0.02])
            for loc in data['location_type']
        ]
        
        # Employment status
        employment_types = ['Formal', 'Informal', 'Self-employed', 'Unemployed', 'Student']
        data['employment_status'] = [
            np.random.choice(employment_types, p=[0.35, 0.30, 0.20, 0.10, 0.05])
            if loc == 'Urban' else
            np.random.choice(employment_types, p=[0.15, 0.45, 0.25, 0.10, 0.05])
            for loc in data['location_type']
        ]
        
        return pd.DataFrame(data)
    
    def generate_financial_features(self, demographics_df):
        """Generate financial and behavioral features"""
        data = demographics_df.copy()
        
        # Monthly income (correlated with education and location)
        base_income = np.random.lognormal(10, 0.8, self.n_samples)
        
        # Apply multipliers based on demographics
        education_multiplier = data['education'].map({
            'Primary': 0.5, 'Secondary': 0.7, 'Certificate': 0.9,
            'Diploma': 1.1, 'Degree': 1.5, 'Postgraduate': 2.0
        })
        
        location_multiplier = data['location_type'].map({'Urban': 1.2, 'Rural': 0.8})
        
        data['monthly_income'] = (base_income * education_multiplier * location_multiplier).clip(5000, 500000)
        
        # Mobile money usage (transactions per month)
        # Urban and younger users transact more
        base_transactions = np.random.poisson(25, self.n_samples)
        age_factor = (50 - data['age']) / 50  # Younger = more transactions
        location_factor = data['location_type'].map({'Urban': 1.3, 'Rural': 0.7})
        
        data['mpesa_transactions_monthly'] = (base_transactions * (1 + age_factor) * location_factor).clip(1, 200).astype(int)
        
        # Average transaction amount
        data['avg_transaction_amount'] = (data['monthly_income'] * 0.15 * np.random.uniform(0.5, 1.5, self.n_samples)).clip(100, 50000)
        
        # Account age (months since registration)
        data['account_age_months'] = np.random.exponential(18, self.n_samples).clip(1, 60).astype(int)
        
        # Loan history
        # Probability of having loan history increases with account age
        loan_history_prob = (data['account_age_months'] / 60).clip(0, 0.85)
        data['previous_loans'] = np.random.binomial(5, loan_history_prob)
        
        # Repayment rate for those with loan history
        data['repayment_rate'] = np.where(
            data['previous_loans'] > 0,
            np.random.beta(8, 2, self.n_samples),  # Most people repay well
            np.nan
        )
        
        # Device characteristics
        device_types = ['Feature_Phone', 'Budget_Smartphone', 'Mid_Range_Smartphone', 'High_End_Smartphone']
        device_probs_urban = [0.05, 0.35, 0.45, 0.15]
        device_probs_rural = [0.20, 0.50, 0.25, 0.05]
        
        data['device_type'] = [
            np.random.choice(device_types, p=device_probs_urban if loc == 'Urban' else device_probs_rural)
            for loc in data['location_type']
        ]
        
        # App usage frequency (days active per month)
        data['app_usage_days'] = np.random.binomial(30, 0.5, self.n_samples)
        
        # Social connections on platform
        data['platform_connections'] = np.random.poisson(8, self.n_samples).clip(0, 50)
        
        return data
    
    def generate_credit_outcomes(self, features_df):
        """
        Generate credit scores and loan approval outcomes
        Intentionally introduce biases to simulate real-world issues
        """
        data = features_df.copy()
        
        # Base credit score calculation (0-100 scale)
        score = 50  # Base score
        
        # Positive factors
        score += (data['monthly_income'] / 10000) * 5  # Income contribution
        score += (data['account_age_months'] / 60) * 10  # Account age
        score += data['repayment_rate'].fillna(0) * 15  # Repayment history
        score += (data['mpesa_transactions_monthly'] / 50) * 5  # Transaction activity
        
        # Add biases (this is where algorithmic bias occurs)
        # Location bias - rural users penalized
        location_penalty = data['location_type'].map({'Urban': 0, 'Rural': -8})
        score += location_penalty
        
        # Device bias - lower-end devices penalized
        device_penalty = data['device_type'].map({
            'Feature_Phone': -6,
            'Budget_Smartphone': -3,
            'Mid_Range_Smartphone': 0,
            'High_End_Smartphone': 2
        })
        score += device_penalty
        
        # Gender bias (subtle)
        gender_bias = data['gender'].map({'M': 1, 'F': -2})
        score += gender_bias
        
        # Add random noise
        score += np.random.normal(0, 5, self.n_samples)
        
        # Clip to 0-100 range
        data['credit_score'] = score.clip(0, 100)
        
        # Loan approval (threshold-based with some randomness)
        approval_threshold = 55
        approval_prob = 1 / (1 + np.exp(-(data['credit_score'] - approval_threshold) / 5))
        data['loan_approved'] = np.random.binomial(1, approval_prob)
        
        # Loan amount offered (for approved loans)
        max_loan = data['monthly_income'] * 2
        data['loan_amount_offered'] = np.where(
            data['loan_approved'] == 1,
            max_loan * (data['credit_score'] / 100) * np.random.uniform(0.8, 1.2, self.n_samples),
            0
        )
        
        # Interest rate (higher score = lower rate)
        base_rate = 15  # Base monthly rate
        data['interest_rate'] = np.where(
            data['loan_approved'] == 1,
            base_rate - ((data['credit_score'] - 50) / 10) + np.random.normal(0, 1, self.n_samples),
            np.nan
        ).clip(8, 25)
        
        return data
    
    def generate_full_dataset(self):
        """Generate complete synthetic dataset"""
        print("Generating demographics...")
        demographics = self.generate_demographics()
        
        print("Generating financial features...")
        with_financials = self.generate_financial_features(demographics)
        
        print("Generating credit outcomes...")
        complete_data = self.generate_credit_outcomes(with_financials)
        
        # Add timestamp
        complete_data['application_date'] = [
            datetime.now() - timedelta(days=random.randint(0, 365))
            for _ in range(self.n_samples)
        ]
        
        print(f"\nDataset generated: {len(complete_data)} records")
        print(f"Columns: {len(complete_data.columns)}")
        
        return complete_data


# Generate the dataset
if __name__ == "__main__":
    generator = DigitalCreditDataGenerator(n_samples=15000)
    df = generator.generate_full_dataset()
    
    # Display summary statistics
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    print(f"\nShape: {df.shape}")
    print(f"\nData types:\n{df.dtypes}")
    print(f"\nFirst few rows:\n{df.head()}")
    print(f"\nBasic statistics:\n{df.describe()}")
    
    # Check for class imbalance
    print(f"\nLoan Approval Distribution:")
    print(df['loan_approved'].value_counts(normalize=True))
    
    print(f"\nApproval Rate by Location:")
    print(df.groupby('location_type')['loan_approved'].mean())
    
    print(f"\nApproval Rate by Gender:")
    print(df.groupby('gender')['loan_approved'].mean())
    
    # Save to CSV
    df.to_csv('synthetic_credit_data.csv', index=False)
    print("\nDataset saved to 'synthetic_credit_data.csv'")
