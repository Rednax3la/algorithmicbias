"""
Phase 2: Exploratory Data Analysis and Bias Detection
======================================================
Analyzes the credit scoring dataset for patterns of algorithmic bias
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class CreditBiasAnalyzer:
    """
    Performs comprehensive bias analysis on credit scoring data
    """
    
    def __init__(self, data_path='synthetic_credit_data.csv'):
        """Load the dataset"""
        self.df = pd.read_csv(data_path)
        self.protected_attributes = ['gender', 'location_type', 'county']
        
        print(f"Dataset loaded: {self.df.shape[0]} records, {self.df.shape[1]} features")
    
    def basic_statistics(self):
        """Generate basic statistical overview"""
        print("\n" + "="*70)
        print("BASIC STATISTICS")
        print("="*70)
        
        # Overall approval rate
        overall_approval = self.df['loan_approved'].mean()
        print(f"\nOverall Loan Approval Rate: {overall_approval:.2%}")
        
        # Credit score distribution
        print(f"\nCredit Score Statistics:")
        print(self.df['credit_score'].describe())
        
        # Missing values
        print(f"\nMissing Values:")
        missing = self.df.isnull().sum()
        print(missing[missing > 0])
        
        return self.df.describe()
    
    def demographic_bias_analysis(self):
        """Analyze bias across demographic groups"""
        print("\n" + "="*70)
        print("DEMOGRAPHIC BIAS ANALYSIS")
        print("="*70)
        
        results = {}
        
        for attr in self.protected_attributes:
            print(f"\n{attr.upper()} Analysis:")
            print("-" * 50)
            
            # Approval rates by group
            approval_by_group = self.df.groupby(attr)['loan_approved'].agg(['mean', 'count'])
            approval_by_group.columns = ['Approval_Rate', 'Count']
            print(f"\nApproval Rates:\n{approval_by_group}")
            
            # Credit scores by group
            score_by_group = self.df.groupby(attr)['credit_score'].agg(['mean', 'std', 'median'])
            print(f"\nCredit Scores:\n{score_by_group}")
            
            # Statistical significance test (Chi-square for approval)
            contingency_table = pd.crosstab(self.df[attr], self.df['loan_approved'])
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            print(f"\nChi-square test for approval independence:")
            print(f"  Chi-square statistic: {chi2:.4f}")
            print(f"  P-value: {p_value:.6f}")
            print(f"  {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'} at α=0.05")
            
            # Effect size (Cramér's V)
            n = contingency_table.sum().sum()
            cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
            print(f"  Cramér's V (effect size): {cramers_v:.4f}")
            
            results[attr] = {
                'approval_rates': approval_by_group,
                'credit_scores': score_by_group,
                'chi2': chi2,
                'p_value': p_value,
                'cramers_v': cramers_v
            }
        
        return results
    
    def disparate_impact_analysis(self):
        """
        Calculate Disparate Impact Ratio (80% rule)
        DIR = (Positive outcome rate for protected group) / (Positive outcome rate for reference group)
        DIR < 0.8 indicates potential discrimination
        """
        print("\n" + "="*70)
        print("DISPARATE IMPACT ANALYSIS (80% Rule)")
        print("="*70)
        
        disparate_impact = {}
        
        # Gender analysis
        print("\nGENDER:")
        male_approval = self.df[self.df['gender'] == 'M']['loan_approved'].mean()
        female_approval = self.df[self.df['gender'] == 'F']['loan_approved'].mean()
        gender_dir = female_approval / male_approval
        
        print(f"  Male approval rate: {male_approval:.4f}")
        print(f"  Female approval rate: {female_approval:.4f}")
        print(f"  Disparate Impact Ratio: {gender_dir:.4f}")
        print(f"  {'⚠️  FAILS 80% rule' if gender_dir < 0.8 else '✓ Passes 80% rule'}")
        
        disparate_impact['gender'] = gender_dir
        
        # Location analysis
        print("\nLOCATION:")
        urban_approval = self.df[self.df['location_type'] == 'Urban']['loan_approved'].mean()
        rural_approval = self.df[self.df['location_type'] == 'Rural']['loan_approved'].mean()
        location_dir = rural_approval / urban_approval
        
        print(f"  Urban approval rate: {urban_approval:.4f}")
        print(f"  Rural approval rate: {rural_approval:.4f}")
        print(f"  Disparate Impact Ratio: {location_dir:.4f}")
        print(f"  {'⚠️  FAILS 80% rule' if location_dir < 0.8 else '✓ Passes 80% rule'}")
        
        disparate_impact['location'] = location_dir
        
        return disparate_impact
    
    def feature_correlation_analysis(self):
        """Analyze correlations between features and outcomes"""
        print("\n" + "="*70)
        print("FEATURE CORRELATION ANALYSIS")
        print("="*70)
        
        # Select numeric features
        numeric_features = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Correlation with credit score
        correlations = self.df[numeric_features].corr()['credit_score'].sort_values(ascending=False)
        
        print("\nTop features correlated with Credit Score:")
        print(correlations.head(10))
        
        print("\nBottom features correlated with Credit Score:")
        print(correlations.tail(5))
        
        return correlations
    
    def income_analysis(self):
        """Analyze income disparities across groups"""
        print("\n" + "="*70)
        print("INCOME DISPARITY ANALYSIS")
        print("="*70)
        
        # Income by location
        print("\nIncome by Location Type:")
        income_by_location = self.df.groupby('location_type')['monthly_income'].agg(['mean', 'median', 'std'])
        print(income_by_location)
        
        # Statistical test
        urban_income = self.df[self.df['location_type'] == 'Urban']['monthly_income']
        rural_income = self.df[self.df['location_type'] == 'Rural']['monthly_income']
        t_stat, p_value = stats.ttest_ind(urban_income, rural_income)
        
        print(f"\nT-test for income difference:")
        print(f"  T-statistic: {t_stat:.4f}")
        print(f"  P-value: {p_value:.6f}")
        
        # Income by gender
        print("\nIncome by Gender:")
        income_by_gender = self.df.groupby('gender')['monthly_income'].agg(['mean', 'median', 'std'])
        print(income_by_gender)
        
    def visualize_bias_patterns(self):
        """Create visualizations for bias analysis"""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Algorithmic Bias Analysis in Digital Credit Scoring', fontsize=16, fontweight='bold')
        
        # 1. Approval rates by location
        approval_by_location = self.df.groupby('location_type')['loan_approved'].mean()
        axes[0, 0].bar(approval_by_location.index, approval_by_location.values, color=['#2ecc71', '#e74c3c'])
        axes[0, 0].set_title('Loan Approval Rate by Location')
        axes[0, 0].set_ylabel('Approval Rate')
        axes[0, 0].axhline(y=0.8 * approval_by_location.max(), color='orange', linestyle='--', label='80% Rule Threshold')
        axes[0, 0].legend()
        
        # 2. Approval rates by gender
        approval_by_gender = self.df.groupby('gender')['loan_approved'].mean()
        axes[0, 1].bar(approval_by_gender.index, approval_by_gender.values, color=['#3498db', '#e91e63'])
        axes[0, 1].set_title('Loan Approval Rate by Gender')
        axes[0, 1].set_ylabel('Approval Rate')
        
        # 3. Credit score distribution by location
        self.df.boxplot(column='credit_score', by='location_type', ax=axes[0, 2])
        axes[0, 2].set_title('Credit Score Distribution by Location')
        axes[0, 2].set_xlabel('Location Type')
        axes[0, 2].set_ylabel('Credit Score')
        
        # 4. Approval rate by device type
        approval_by_device = self.df.groupby('device_type')['loan_approved'].mean().sort_values()
        axes[1, 0].barh(approval_by_device.index, approval_by_device.values, color='skyblue')
        axes[1, 0].set_title('Loan Approval Rate by Device Type')
        axes[1, 0].set_xlabel('Approval Rate')
        
        # 5. Income vs Credit Score colored by location
        urban = self.df[self.df['location_type'] == 'Urban']
        rural = self.df[self.df['location_type'] == 'Rural']
        axes[1, 1].scatter(urban['monthly_income'], urban['credit_score'], alpha=0.5, label='Urban', s=10)
        axes[1, 1].scatter(rural['monthly_income'], rural['credit_score'], alpha=0.5, label='Rural', s=10)
        axes[1, 1].set_title('Income vs Credit Score')
        axes[1, 1].set_xlabel('Monthly Income')
        axes[1, 1].set_ylabel('Credit Score')
        axes[1, 1].legend()
        
        # 6. Approval rate by county
        approval_by_county = self.df.groupby('county')['loan_approved'].mean().sort_values()
        axes[1, 2].barh(approval_by_county.index, approval_by_county.values, color='coral')
        axes[1, 2].set_title('Loan Approval Rate by County')
        axes[1, 2].set_xlabel('Approval Rate')
        
        plt.tight_layout()
        plt.savefig('bias_analysis_visualizations.png', dpi=300, bbox_inches='tight')
        print("\nVisualizations saved to 'bias_analysis_visualizations.png'")
        plt.show()
    
    def generate_bias_report(self):
        """Generate comprehensive bias audit report"""
        print("\n" + "="*70)
        print("COMPREHENSIVE BIAS AUDIT REPORT")
        print("="*70)
        
        # Run all analyses
        self.basic_statistics()
        demo_results = self.demographic_bias_analysis()
        di_results = self.disparate_impact_analysis()
        self.feature_correlation_analysis()
        self.income_analysis()
        
        # Generate summary
        print("\n" + "="*70)
        print("SUMMARY OF FINDINGS")
        print("="*70)
        
        print("\n🔍 KEY BIAS INDICATORS:")
        
        if di_results['location'] < 0.8:
            print(f"\n⚠️  LOCATION BIAS DETECTED")
            print(f"   Rural applicants are {(1 - di_results['location']) * 100:.1f}% less likely to be approved than urban applicants")
        
        if di_results['gender'] < 0.8:
            print(f"\n⚠️  GENDER BIAS DETECTED")
            print(f"   Female applicants are {(1 - di_results['gender']) * 100:.1f}% less likely to be approved than male applicants")
        
        # Visualizations
        self.visualize_bias_patterns()


# Run the analysis
if __name__ == "__main__":
    analyzer = CreditBiasAnalyzer('synthetic_credit_data.csv')
    analyzer.generate_bias_report()
