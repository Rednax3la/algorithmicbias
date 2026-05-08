"""
Phase 4: Explainable AI Analysis using SHAP
============================================
Analyzes feature importance and individual predictions using SHAP values
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

class ExplainableCreditModel:
    """
    Provides interpretability analysis for credit scoring models
    """
    
    def __init__(self, trained_model, X_train, X_test, feature_names):
        """
        Initialize with a trained model
        
        Args:
            trained_model: Trained sklearn model
            X_train: Training features
            X_test: Test features
            feature_names: List of feature names
        """
        self.model = trained_model
        self.X_train = X_train
        self.X_test = X_test
        self.feature_names = feature_names
        
        print("Explainable AI module initialized")
    
    def compute_feature_importance(self):
        """Calculate and visualize feature importance"""
        print("\n" + "="*70)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("="*70)
        
        # Method 1: Model's built-in feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            print("\nModel's Built-in Feature Importance:")
            
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print(importance_df.head(15))
            
            # Visualize
            plt.figure(figsize=(10, 8))
            plt.barh(importance_df['feature'].head(15), 
                    importance_df['importance'].head(15))
            plt.xlabel('Importance')
            plt.title('Top 15 Features by Model Importance')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig('feature_importance_builtin.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            self.feature_importance = importance_df
        
        # Method 2: Permutation Importance
        print("\nComputing Permutation Importance...")
        perm_importance = permutation_importance(
            self.model, self.X_test, 
            np.array(self.X_test.index.map(lambda x: 1)),  # Dummy target for demo
            n_repeats=10,
            random_state=42
        )
        
        perm_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance_mean': perm_importance.importances_mean,
            'importance_std': perm_importance.importances_std
        }).sort_values('importance_mean', ascending=False)
        
        print("\nPermutation Importance (Top 15):")
        print(perm_importance_df.head(15))
        
        return importance_df if hasattr(self.model, 'feature_importances_') else perm_importance_df
    
    def shap_analysis(self, sample_size=500):
        """
        Perform SHAP analysis for model interpretability
        
        Args:
            sample_size: Number of samples to use for SHAP (for computational efficiency)
        """
        print("\n" + "="*70)
        print("SHAP (SHapley Additive exPlanations) ANALYSIS")
        print("="*70)
        
        # Sample data for efficiency
        if len(self.X_test) > sample_size:
            sample_indices = np.random.choice(len(self.X_test), sample_size, replace=False)
            X_sample = self.X_test.iloc[sample_indices]
        else:
            X_sample = self.X_test
        
        print(f"\nAnalyzing {len(X_sample)} samples...")
        
        # Create SHAP explainer
        # For tree-based models, use TreeExplainer (faster)
        if hasattr(self.model, 'estimators_'):
            print("Using TreeExplainer (optimized for tree-based models)...")
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_sample)
            
            # For binary classification, get positive class SHAP values
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
        else:
            # For other models, use KernelExplainer
            print("Using KernelExplainer...")
            # Use a background dataset (sample from training data)
            background = shap.sample(self.X_train, 100)
            explainer = shap.KernelExplainer(self.model.predict_proba, background)
            shap_values = explainer.shap_values(X_sample)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
        
        self.shap_values = shap_values
        self.shap_sample = X_sample
        self.explainer = explainer
        
        print("✓ SHAP values computed successfully")
        
        return shap_values, X_sample
    
    def visualize_shap_summary(self):
        """Create SHAP summary plots"""
        print("\nGenerating SHAP visualizations...")
        
        # Summary plot (bee swarm)
        plt.figure(figsize=(10, 8))
        shap.summary_plot(self.shap_values, self.shap_sample, 
                         feature_names=self.feature_names,
                         plot_type="dot", show=False)
        plt.tight_layout()
        plt.savefig('shap_summary_beeswarm.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Bar plot of mean absolute SHAP values
        plt.figure(figsize=(10, 8))
        shap.summary_plot(self.shap_values, self.shap_sample,
                         feature_names=self.feature_names,
                         plot_type="bar", show=False)
        plt.tight_layout()
        plt.savefig('shap_summary_bar.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✓ SHAP visualizations saved")
    
    def analyze_individual_predictions(self, n_samples=5):
        """
        Analyze SHAP values for individual predictions
        
        Args:
            n_samples: Number of individual predictions to visualize
        """
        print("\n" + "="*70)
        print("INDIVIDUAL PREDICTION ANALYSIS")
        print("="*70)
        
        # Select diverse samples (approved and rejected)
        sample_indices = np.random.choice(len(self.shap_sample), 
                                         min(n_samples, len(self.shap_sample)), 
                                         replace=False)
        
        for idx in sample_indices[:3]:  # Show first 3 for brevity
            print(f"\nSample {idx}:")
            
            # Get prediction
            sample_data = self.shap_sample.iloc[idx:idx+1]
            prediction = self.model.predict(sample_data)[0]
            probability = self.model.predict_proba(sample_data)[0]
            
            print(f"  Prediction: {'Approved' if prediction == 1 else 'Rejected'}")
            print(f"  Probability: {probability[1]:.4f}")
            
            # Waterfall plot
            plt.figure(figsize=(10, 6))
            shap.waterfall_plot(
                shap.Explanation(
                    values=self.shap_values[idx],
                    base_values=self.explainer.expected_value if hasattr(self.explainer, 'expected_value') else 0,
                    data=self.shap_sample.iloc[idx],
                    feature_names=self.feature_names
                ),
                show=False
            )
            plt.tight_layout()
            plt.savefig(f'shap_waterfall_sample_{idx}.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def analyze_bias_features(self, protected_test_data):
        """
        Analyze how protected attributes influence predictions via SHAP
        
        Args:
            protected_test_data: DataFrame with protected attributes
        """
        print("\n" + "="*70)
        print("BIAS FEATURE ANALYSIS")
        print("="*70)
        
        # Map SHAP sample indices back to protected attributes
        protected_sample = protected_test_data.iloc[self.shap_sample.index]
        
        # Analyze SHAP values by protected groups
        for attr in ['gender', 'location_type']:
            print(f"\n{attr.upper()} Analysis:")
            print("-" * 50)
            
            # Get mean SHAP values for each group
            groups = protected_sample[attr].unique()
            
            for group in groups:
                group_mask = protected_sample[attr] == group
                group_shap = self.shap_values[group_mask]
                
                # Mean absolute SHAP value across all features
                mean_abs_shap = np.abs(group_shap).mean(axis=0)
                
                # Top features for this group
                top_features_idx = np.argsort(mean_abs_shap)[-5:][::-1]
                
                print(f"\n  {group}:")
                print(f"    Sample size: {group_mask.sum()}")
                print(f"    Top influential features:")
                for i, idx in enumerate(top_features_idx, 1):
                    print(f"      {i}. {self.feature_names[idx]}: "
                          f"{mean_abs_shap[idx]:.4f}")
        
        # Visualize SHAP distribution by protected group
        self._plot_shap_by_group(protected_sample)
    
    def _plot_shap_by_group(self, protected_sample):
        """Plot SHAP value distributions by protected groups"""
        
        # Get top 5 most important features overall
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        top_features_idx = np.argsort(mean_abs_shap)[-5:][::-1]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('SHAP Value Distribution by Protected Groups', 
                    fontsize=14, fontweight='bold')
        axes = axes.flatten()
        
        # Plot for top features
        for i, feat_idx in enumerate(top_features_idx):
            feature_name = self.feature_names[feat_idx]
            
            # Location group comparison
            urban_mask = protected_sample['location_type'] == 'Urban'
            rural_mask = protected_sample['location_type'] == 'Rural'
            
            axes[i].hist(self.shap_values[urban_mask, feat_idx], 
                        alpha=0.6, bins=30, label='Urban', color='blue')
            axes[i].hist(self.shap_values[rural_mask, feat_idx], 
                        alpha=0.6, bins=30, label='Rural', color='red')
            axes[i].set_title(f'{feature_name}')
            axes[i].set_xlabel('SHAP Value')
            axes[i].set_ylabel('Frequency')
            axes[i].legend()
            axes[i].axvline(x=0, color='black', linestyle='--', alpha=0.3)
        
        # Hide last subplot if not used
        if len(top_features_idx) < 6:
            axes[5].axis('off')
        
        plt.tight_layout()
        plt.savefig('shap_by_protected_group.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\n✓ Protected group SHAP analysis saved")
    
    def generate_bias_report(self):
        """Generate summary of bias-related findings from SHAP"""
        print("\n" + "="*70)
        print("BIAS INSIGHTS FROM SHAP ANALYSIS")
        print("="*70)
        
        # Calculate feature importance
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        feature_ranking = pd.DataFrame({
            'feature': self.feature_names,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=False)
        
        print("\nTop 10 Most Influential Features:")
        print(feature_ranking.head(10))
        
        # Check if protected attributes are directly influential
        protected_features = [f for f in self.feature_names 
                            if any(p in f for p in ['gender', 'location'])]
        
        if protected_features:
            print(f"\nProtected Attribute Influence:")
            for feat in protected_features:
                rank = feature_ranking[feature_ranking['feature'] == feat].index[0] + 1
                importance = feature_ranking[feature_ranking['feature'] == feat]['mean_abs_shap'].values[0]
                print(f"  {feat}: Rank #{rank}, Importance: {importance:.4f}")
        
        print("\n" + "="*70)


# Example usage function
def run_explainability_analysis(model_dict, X_train, X_test, y_test, 
                               feature_names, protected_test):
    """
    Run complete explainability analysis
    
    Args:
        model_dict: Dictionary containing trained model
        X_train, X_test: Feature matrices
        y_test: Test labels
        feature_names: List of feature names
        protected_test: DataFrame with protected attributes
    """
    
    # Initialize explainer
    explainer = ExplainableCreditModel(
        model_dict['model'],
        X_train,
        X_test,
        feature_names
    )
    
    # Run analyses
    explainer.compute_feature_importance()
    explainer.shap_analysis(sample_size=500)
    explainer.visualize_shap_summary()
    explainer.analyze_individual_predictions(n_samples=5)
    explainer.analyze_bias_features(protected_test)
    explainer.generate_bias_report()
    
    print("\n✓ Explainability analysis complete")
    print("\nGenerated files:")
    print("  - feature_importance_builtin.png")
    print("  - shap_summary_beeswarm.png")
    print("  - shap_summary_bar.png")
    print("  - shap_waterfall_sample_*.png")
    print("  - shap_by_protected_group.png")
    
    return explainer


# Standalone execution example
if __name__ == "__main__":
    print("This module should be imported and used with a trained model")
    print("Example usage:")
    print("""
    from phase3_models import FairCreditScoringModel
    from phase4_explainability import run_explainability_analysis
    
    # Train model
    model = FairCreditScoringModel('synthetic_credit_data.csv')
    model.run_full_analysis()
    
    # Run explainability
    rf_model = model.models['Random Forest']
    explainer = run_explainability_analysis(
        rf_model,
        model.X_train,
        model.X_test,
        model.y_test,
        model.feature_names,
        model.protected_test
    )
    """)
