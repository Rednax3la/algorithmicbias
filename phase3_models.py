"""
Phase 3: Machine Learning Models with Fairness Evaluation
==========================================================
Builds classification models and evaluates them for bias and fairness
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix, 
                            classification_report)
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class FairCreditScoringModel:
    """
    Trains credit scoring models and evaluates fairness metrics
    """
    
    def __init__(self, data_path='synthetic_credit_data.csv'):
        """Load and prepare data"""
        self.df = pd.read_csv(data_path)
        self.models = {}
        self.results = {}
        
        print(f"Dataset loaded: {self.df.shape}")
    
    def preprocess_data(self):
        """Prepare features for modeling"""
        print("\n" + "="*70)
        print("DATA PREPROCESSING")
        print("="*70)
        
        # Create a copy
        df_model = self.df.copy()
        
        # Select features for modeling
        feature_cols = [
            'age', 'monthly_income', 'mpesa_transactions_monthly',
            'avg_transaction_amount', 'account_age_months', 
            'previous_loans', 'app_usage_days', 'platform_connections',
            'gender', 'location_type', 'education', 'employment_status',
            'device_type'
        ]
        
        # Handle missing values in repayment_rate
        df_model['repayment_rate'] = df_model['repayment_rate'].fillna(0)
        feature_cols.append('repayment_rate')
        
        # Encode categorical variables
        label_encoders = {}
        categorical_cols = ['gender', 'location_type', 'education', 
                           'employment_status', 'device_type']
        
        for col in categorical_cols:
            le = LabelEncoder()
            df_model[col + '_encoded'] = le.fit_transform(df_model[col])
            label_encoders[col] = le
        
        # Create feature matrix
        feature_cols_encoded = [col for col in feature_cols if col not in categorical_cols]
        feature_cols_encoded += [col + '_encoded' for col in categorical_cols]
        
        X = df_model[feature_cols_encoded]
        y = df_model['loan_approved']
        
        # Store protected attributes separately
        self.protected_attrs = df_model[['gender', 'location_type', 'county']]
        
        print(f"\nFeatures selected: {len(feature_cols_encoded)}")
        print(f"Feature names: {feature_cols_encoded}")
        print(f"\nTarget distribution:")
        print(y.value_counts(normalize=True))
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Split protected attributes accordingly
        self.protected_train = self.protected_attrs.iloc[X_train.index]
        self.protected_test = self.protected_attrs.iloc[X_test.index]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Convert back to DataFrame for easier handling
        self.X_train = pd.DataFrame(X_train_scaled, columns=X.columns)
        self.X_test = pd.DataFrame(X_test_scaled, columns=X.columns)
        self.y_train = y_train.values
        self.y_test = y_test.values
        
        self.feature_names = X.columns.tolist()
        self.scaler = scaler
        self.label_encoders = label_encoders
        
        print(f"\nTrain set size: {len(self.X_train)}")
        print(f"Test set size: {len(self.X_test)}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def train_models(self):
        """Train multiple classification models"""
        print("\n" + "="*70)
        print("MODEL TRAINING")
        print("="*70)
        
        # Define models
        models_to_train = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }
        
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...")
            
            # Train
            model.fit(self.X_train, self.y_train)
            
            # Predictions
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)[:, 1]
            
            # Store
            self.models[name] = {
                'model': model,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
            print(f"  ✓ {name} trained successfully")
        
        return self.models
    
    def evaluate_performance(self):
        """Evaluate standard ML metrics"""
        print("\n" + "="*70)
        print("MODEL PERFORMANCE EVALUATION")
        print("="*70)
        
        for name, model_dict in self.models.items():
            y_pred = model_dict['predictions']
            y_pred_proba = model_dict['probabilities']
            
            print(f"\n{name}:")
            print("-" * 50)
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred)
            recall = recall_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred)
            roc_auc = roc_auc_score(self.y_test, y_pred_proba)
            
            print(f"Accuracy:  {accuracy:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall:    {recall:.4f}")
            print(f"F1 Score:  {f1:.4f}")
            print(f"ROC AUC:   {roc_auc:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(self.y_test, y_pred)
            print(f"\nConfusion Matrix:")
            print(cm)
            
            # Store results
            self.results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'roc_auc': roc_auc,
                'confusion_matrix': cm
            }
    
    def evaluate_fairness(self):
        """Evaluate fairness metrics across protected groups"""
        print("\n" + "="*70)
        print("FAIRNESS EVALUATION")
        print("="*70)
        
        fairness_results = {}
        
        for model_name, model_dict in self.models.items():
            print(f"\n{model_name}:")
            print("-" * 50)
            
            y_pred = model_dict['predictions']
            
            fairness_results[model_name] = {}
            
            # Evaluate for each protected attribute
            for attr in ['gender', 'location_type']:
                print(f"\n  {attr.upper()} Fairness:")
                
                groups = self.protected_test[attr].unique()
                group_metrics = {}
                
                for group in groups:
                    # Get indices for this group
                    group_mask = self.protected_test[attr] == group
                    
                    # Calculate metrics for this group
                    if group_mask.sum() > 0:
                        y_true_group = self.y_test[group_mask]
                        y_pred_group = y_pred[group_mask]
                        
                        # Positive prediction rate (selection rate)
                        selection_rate = y_pred_group.mean()
                        
                        # True positive rate (recall/sensitivity)
                        if y_true_group.sum() > 0:
                            tpr = recall_score(y_true_group, y_pred_group, zero_division=0)
                        else:
                            tpr = 0
                        
                        # False positive rate
                        tn, fp, fn, tp = confusion_matrix(y_true_group, y_pred_group, 
                                                          labels=[0, 1]).ravel()
                        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                        
                        # Precision for this group
                        prec = precision_score(y_true_group, y_pred_group, zero_division=0)
                        
                        group_metrics[group] = {
                            'selection_rate': selection_rate,
                            'tpr': tpr,
                            'fpr': fpr,
                            'precision': prec,
                            'count': group_mask.sum()
                        }
                        
                        print(f"    {group}:")
                        print(f"      Selection Rate: {selection_rate:.4f}")
                        print(f"      TPR (Recall):   {tpr:.4f}")
                        print(f"      FPR:            {fpr:.4f}")
                        print(f"      Precision:      {prec:.4f}")
                        print(f"      Sample Size:    {group_mask.sum()}")
                
                # Calculate fairness metrics
                if len(group_metrics) == 2:
                    groups_list = list(group_metrics.keys())
                    
                    # Statistical Parity Difference
                    spd = (group_metrics[groups_list[0]]['selection_rate'] - 
                           group_metrics[groups_list[1]]['selection_rate'])
                    
                    # Disparate Impact
                    di = (group_metrics[groups_list[1]]['selection_rate'] / 
                          group_metrics[groups_list[0]]['selection_rate'])
                    
                    # Equal Opportunity Difference (TPR difference)
                    eod = (group_metrics[groups_list[0]]['tpr'] - 
                           group_metrics[groups_list[1]]['tpr'])
                    
                    print(f"\n  Fairness Metrics ({attr}):")
                    print(f"    Statistical Parity Difference: {spd:.4f} (ideal: 0)")
                    print(f"    Disparate Impact Ratio: {di:.4f} (ideal: 1.0, min: 0.8)")
                    print(f"    Equal Opportunity Difference: {eod:.4f} (ideal: 0)")
                    
                    if abs(spd) > 0.1:
                        print(f"    ⚠️  Significant statistical parity violation")
                    if di < 0.8:
                        print(f"    ⚠️  Fails 80% rule for disparate impact")
                    if abs(eod) > 0.1:
                        print(f"    ⚠️  Significant equal opportunity violation")
                    
                    fairness_results[model_name][attr] = {
                        'group_metrics': group_metrics,
                        'spd': spd,
                        'disparate_impact': di,
                        'eod': eod
                    }
        
        self.fairness_results = fairness_results
        return fairness_results
    
    def visualize_fairness(self):
        """Create visualizations for fairness comparison"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Model Fairness Comparison', fontsize=16, fontweight='bold')
        
        # Prepare data for plotting
        models = list(self.fairness_results.keys())
        
        # 1. Disparate Impact by Location
        di_location = [self.fairness_results[m]['location_type']['disparate_impact'] 
                      for m in models]
        axes[0, 0].bar(models, di_location, color='skyblue')
        axes[0, 0].axhline(y=0.8, color='red', linestyle='--', label='80% Rule Threshold')
        axes[0, 0].axhline(y=1.0, color='green', linestyle='--', label='Perfect Parity')
        axes[0, 0].set_title('Disparate Impact - Location Type')
        axes[0, 0].set_ylabel('Disparate Impact Ratio')
        axes[0, 0].legend()
        axes[0, 0].tick_params(axis='x', rotation=15)
        
        # 2. Disparate Impact by Gender
        di_gender = [self.fairness_results[m]['gender']['disparate_impact'] 
                    for m in models]
        axes[0, 1].bar(models, di_gender, color='lightcoral')
        axes[0, 1].axhline(y=0.8, color='red', linestyle='--', label='80% Rule Threshold')
        axes[0, 1].axhline(y=1.0, color='green', linestyle='--', label='Perfect Parity')
        axes[0, 1].set_title('Disparate Impact - Gender')
        axes[0, 1].set_ylabel('Disparate Impact Ratio')
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=15)
        
        # 3. Statistical Parity Difference
        spd_location = [abs(self.fairness_results[m]['location_type']['spd']) 
                       for m in models]
        spd_gender = [abs(self.fairness_results[m]['gender']['spd']) 
                     for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        axes[1, 0].bar(x - width/2, spd_location, width, label='Location', color='skyblue')
        axes[1, 0].bar(x + width/2, spd_gender, width, label='Gender', color='lightcoral')
        axes[1, 0].set_title('Statistical Parity Difference (Absolute)')
        axes[1, 0].set_ylabel('Absolute SPD')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(models, rotation=15)
        axes[1, 0].legend()
        axes[1, 0].axhline(y=0.1, color='orange', linestyle='--', alpha=0.5)
        
        # 4. Model Performance vs Fairness Trade-off
        accuracies = [self.results[m]['accuracy'] for m in models]
        avg_di = [(di_location[i] + di_gender[i])/2 for i in range(len(models))]
        
        axes[1, 1].scatter(accuracies, avg_di, s=200, alpha=0.6, c=['blue', 'green', 'red'])
        for i, model in enumerate(models):
            axes[1, 1].annotate(model, (accuracies[i], avg_di[i]), 
                              fontsize=9, ha='center')
        axes[1, 1].axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='80% Rule')
        axes[1, 1].axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Perfect Parity')
        axes[1, 1].set_xlabel('Model Accuracy')
        axes[1, 1].set_ylabel('Average Disparate Impact')
        axes[1, 1].set_title('Accuracy vs Fairness Trade-off')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('fairness_comparison.png', dpi=300, bbox_inches='tight')
        print("\nFairness visualizations saved to 'fairness_comparison.png'")
        plt.show()
    
    def run_full_analysis(self):
        """Execute complete modeling and fairness evaluation pipeline"""
        self.preprocess_data()
        self.train_models()
        self.evaluate_performance()
        self.evaluate_fairness()
        self.visualize_fairness()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print("\nKey files generated:")
        print("  - fairness_comparison.png")


# Run the analysis
if __name__ == "__main__":
    model = FairCreditScoringModel('synthetic_credit_data.csv')
    model.run_full_analysis()
