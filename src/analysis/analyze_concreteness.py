"""
Analyze relationship between code concreteness and LLM performance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import f1_score, accuracy_score
from scipy import stats
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load concreteness data
print("Loading concreteness data...")
concreteness = pd.read_excel('data/processed/concreteness.xlsx')
concreteness['Word'] = concreteness['Word'].str.lower()

# Code names
codes = [
    'Scholar',
    'Activist',
    'Monumental Memorialization',
    'Mention of Scholarly Work',
    'Social/Political Advocacy',
    'Coalition Building',
    'Out of the Mouth of Academics',
    'Out of the Mouth of Activists',
    'Collective Synecdoche'
]

def get_concreteness(text):
    """
    Get concreteness score for a text (word or phrase).
    For multi-word phrases, average the concreteness of constituent words.
    """
    words = text.lower().split()
    scores = []

    for word in words:
        # Skip common words that don't carry semantic meaning
        if word in ['of', 'the', 'a', 'an']:
            continue
        match = concreteness[concreteness['Word'] == word]
        if not match.empty:
            scores.append(match.iloc[0]['Conc.M'])

    if scores:
        return np.mean(scores)
    else:
        return np.nan

def calculate_f1_and_accuracy(gold_standard, model_predictions, code_col):
    """Calculate F1 score and accuracy for a single code."""
    # Ensure we're only looking at the test set (IDs 9-119)
    gold_test = gold_standard[gold_standard['id'].between(9, 119)].copy()
    model_test = model_predictions[model_predictions['id'].between(9, 119)].copy()

    # Sort by ID to ensure alignment
    gold_test = gold_test.sort_values('id').reset_index(drop=True)
    model_test = model_test.sort_values('id').reset_index(drop=True)

    # Merge on ID to ensure we only compare coded passages
    merged = gold_test[['id', code_col]].merge(
        model_test[['id', code_col]],
        on='id',
        suffixes=('_gold', '_pred')
    )

    # Drop any rows with NaN in either gold standard or predictions
    merged = merged.dropna(subset=[f'{code_col}_gold', f'{code_col}_pred'])

    if len(merged) == 0:
        return np.nan, np.nan

    y_true = merged[f'{code_col}_gold'].values
    y_pred = merged[f'{code_col}_pred'].values

    f1 = f1_score(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)

    return f1, acc


def calculate_regression_stats(X, y):
    """Calculate regression statistics including p-values."""
    # Fit regression
    reg = LinearRegression()
    reg.fit(X, y)

    # Get predictions
    y_pred = reg.predict(X)

    # Calculate residuals
    residuals = y - y_pred

    # Degrees of freedom
    n = len(y)
    p = X.shape[1]  # number of predictors
    df_residuals = n - p - 1

    # Mean squared error
    mse = np.sum(residuals**2) / df_residuals

    # Standard error of coefficients
    # For simple linear regression: SE = sqrt(MSE / sum((x - x_mean)^2))
    X_centered = X - X.mean()
    se_slope = np.sqrt(mse / np.sum(X_centered**2))

    # t-statistic and p-value for slope
    t_stat = reg.coef_[0] / se_slope
    p_value_slope = 2 * (1 - stats.t.cdf(abs(t_stat), df_residuals))

    # Standard error for intercept
    se_intercept = np.sqrt(mse * (1/n + X.mean()**2 / np.sum(X_centered**2)))

    # t-statistic and p-value for intercept
    t_stat_intercept = reg.intercept_ / se_intercept
    p_value_intercept = 2 * (1 - stats.t.cdf(abs(t_stat_intercept), df_residuals))

    return {
        'model': reg,
        'slope': reg.coef_[0],
        'intercept': reg.intercept_,
        'r_squared': reg.score(X, y),
        'p_value_slope': p_value_slope,
        'p_value_intercept': p_value_intercept,
        'se_slope': se_slope,
        'se_intercept': se_intercept
    }

# Get concreteness scores for each code
print("\nCalculating concreteness scores for each code...")
code_concreteness = []
for code in codes:
    score = get_concreteness(code)
    code_concreteness.append({
        'code': code,
        'concreteness': score
    })
    print(f"  {code}: {score:.2f}" if not np.isnan(score) else f"  {code}: N/A")

concreteness_df = pd.DataFrame(code_concreteness)

# Load gold standard and GPT-4 predictions
print("\nLoading model results...")
gold_standard = pd.read_csv('data/processed/gold_standard_coding.csv')
gpt4 = pd.read_csv('results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv')

# Calculate F1 and accuracy for each code
print("\nCalculating performance metrics...")
results = []
for code in codes:
    f1, acc = calculate_f1_and_accuracy(gold_standard, gpt4, code)
    conc = concreteness_df[concreteness_df['code'] == code]['concreteness'].values[0]
    results.append({
        'Code': code,
        'Concreteness': conc,
        'F1': f1,
        'Accuracy': acc
    })
    print(f"  {code}: F1={f1:.3f}, Acc={acc:.3f}, Conc={conc:.2f}" if not np.isnan(conc) else f"  {code}: F1={f1:.3f}, Acc={acc:.3f}, Conc=N/A")

results_df = pd.DataFrame(results)

# Remove any codes with missing concreteness scores
results_df_clean = results_df.dropna(subset=['Concreteness'])

print(f"\n{len(results_df_clean)} out of {len(results_df)} codes have concreteness scores")

# Save results
results_df.to_csv('results/outputs/code_concreteness_analysis.csv', index=False)
print("\n✓ Saved analysis to results/outputs/code_concreteness_analysis.csv")

# Create visualization with F1 score
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Concreteness vs F1 Score
if len(results_df_clean) > 1:
    # Fit regression line with statistics
    X = results_df_clean['Concreteness'].values.reshape(-1, 1)
    y_f1 = results_df_clean['F1'].values

    reg_stats_f1 = calculate_regression_stats(X, y_f1)

    # Generate regression line points
    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line_f1 = reg_stats_f1['model'].predict(x_line)

    # Plot scatter
    ax1.scatter(results_df_clean['Concreteness'], results_df_clean['F1'],
                s=150, alpha=0.6, c='steelblue', edgecolors='black', linewidth=1.5)

    # Format p-value
    p_slope_f1 = reg_stats_f1['p_value_slope']
    p_str_f1 = f'p = {p_slope_f1:.3f}' if p_slope_f1 >= 0.001 else 'p < 0.001'

    # Plot regression line
    ax1.plot(x_line, y_line_f1, 'r--', linewidth=2, alpha=0.8,
             label=f'y = {reg_stats_f1["slope"]:.3f}x + {reg_stats_f1["intercept"]:.3f}\nR² = {reg_stats_f1["r_squared"]:.3f}, {p_str_f1}')

    # Add labels for each point
    for _, row in results_df_clean.iterrows():
        ax1.annotate(row['Code'],
                    (row['Concreteness'], row['F1']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.7)

    ax1.set_xlabel('Code Concreteness (Mean)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('F1 Score', fontsize=12, fontweight='bold')
    ax1.set_title('GPT-4 Performance vs Code Concreteness\n(F1 Score)',
                 fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

# Plot 2: Concreteness vs Accuracy
if len(results_df_clean) > 1:
    # Fit regression line with statistics
    y_acc = results_df_clean['Accuracy'].values

    reg_stats_acc = calculate_regression_stats(X, y_acc)

    y_line_acc = reg_stats_acc['model'].predict(x_line)

    # Plot scatter
    ax2.scatter(results_df_clean['Concreteness'], results_df_clean['Accuracy'],
                s=150, alpha=0.6, c='darkgreen', edgecolors='black', linewidth=1.5)

    # Format p-value
    p_slope_acc = reg_stats_acc['p_value_slope']
    p_str_acc = f'p = {p_slope_acc:.3f}' if p_slope_acc >= 0.001 else 'p < 0.001'

    # Plot regression line
    ax2.plot(x_line, y_line_acc, 'r--', linewidth=2, alpha=0.8,
             label=f'y = {reg_stats_acc["slope"]:.3f}x + {reg_stats_acc["intercept"]:.3f}\nR² = {reg_stats_acc["r_squared"]:.3f}, {p_str_acc}')

    # Add labels for each point
    for _, row in results_df_clean.iterrows():
        ax2.annotate(row['Code'],
                    (row['Concreteness'], row['Accuracy']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.7)

    ax2.set_xlabel('Code Concreteness (Mean)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax2.set_title('GPT-4 Performance vs Code Concreteness\n(Accuracy)',
                 fontsize=14, fontweight='bold')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/figures/concreteness_vs_performance.png', dpi=300, bbox_inches='tight')
print("✓ Saved visualization to results/figures/concreteness_vs_performance.png")

# Print summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"\nCorrelation between Concreteness and F1: {results_df_clean['Concreteness'].corr(results_df_clean['F1']):.3f}")
print(f"Correlation between Concreteness and Accuracy: {results_df_clean['Concreteness'].corr(results_df_clean['Accuracy']):.3f}")
print(f"\nMean Concreteness: {results_df_clean['Concreteness'].mean():.2f} (SD: {results_df_clean['Concreteness'].std():.2f})")
print(f"Mean F1: {results_df_clean['F1'].mean():.3f} (SD: {results_df_clean['F1'].std():.3f})")
print(f"Mean Accuracy: {results_df_clean['Accuracy'].mean():.3f} (SD: {results_df_clean['Accuracy'].std():.3f})")

# Print detailed regression statistics
print("\n" + "="*80)
print("REGRESSION STATISTICS")
print("="*80)

print("\n--- Predicting F1 Score from Concreteness ---")
print(f"Slope (β): {reg_stats_f1['slope']:.4f} (SE = {reg_stats_f1['se_slope']:.4f})")
print(f"  p-value: {reg_stats_f1['p_value_slope']:.4f}")
print(f"Intercept: {reg_stats_f1['intercept']:.4f} (SE = {reg_stats_f1['se_intercept']:.4f})")
print(f"  p-value: {reg_stats_f1['p_value_intercept']:.4f}")
print(f"R²: {reg_stats_f1['r_squared']:.4f}")
print(f"N: {len(results_df_clean)}")

print("\n--- Predicting Accuracy from Concreteness ---")
print(f"Slope (β): {reg_stats_acc['slope']:.4f} (SE = {reg_stats_acc['se_slope']:.4f})")
print(f"  p-value: {reg_stats_acc['p_value_slope']:.4f}")
print(f"Intercept: {reg_stats_acc['intercept']:.4f} (SE = {reg_stats_acc['se_intercept']:.4f})")
print(f"  p-value: {reg_stats_acc['p_value_intercept']:.4f}")
print(f"R²: {reg_stats_acc['r_squared']:.4f}")
print(f"N: {len(results_df_clean)}")

print("\n" + "="*80)
print("DONE")
print("="*80)
