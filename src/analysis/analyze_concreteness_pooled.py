"""
Pooled regression analysis: All models combined
Analyzing F1 and Accuracy vs Concreteness with all models' data pooled together
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
plt.rcParams['figure.figsize'] = (16, 6)

print("="*80)
print("POOLED REGRESSION ANALYSIS: All Models Combined")
print("="*80)

# Load data
results_df = pd.read_csv('results/outputs/code_concreteness_analysis_with_gemini.csv')
results_df_clean = results_df.dropna(subset=['Concreteness'])

# Create long-format dataset with all models
data_long = []

models = [
    ('GPT-4', 'F1_GPT4', 'Acc_GPT4'),
    ('GPT-3.5', 'F1_GPT35', 'Acc_GPT35'),
    ('Gemini', 'F1_Gemini', 'Acc_Gemini'),
    ('Llama', 'F1_Llama', 'Acc_Llama')
]

for _, row in results_df_clean.iterrows():
    code = row['Code']
    conc = row['Concreteness']

    for model_name, f1_col, acc_col in models:
        data_long.append({
            'Code': code,
            'Model': model_name,
            'Concreteness': conc,
            'F1': row[f1_col],
            'Accuracy': row[acc_col]
        })

pooled_df = pd.DataFrame(data_long)
total_obs = len(pooled_df)

expected_obs = len(results_df_clean) * len(models)
print(f"\nPooled dataset: {len(pooled_df)} observations (expected {expected_obs} = {len(results_df_clean)} codes × {len(models)} models)")
print(f"Models: {pooled_df['Model'].unique()}")

# Regression function with full statistics
def calculate_regression_stats(X, y):
    """Calculate regression statistics including p-values."""
    reg = LinearRegression()
    reg.fit(X, y)
    y_pred = reg.predict(X)
    residuals = y - y_pred

    n = len(y)
    p = X.shape[1]
    df_residuals = n - p - 1

    mse = np.sum(residuals**2) / df_residuals
    X_centered = X - X.mean()
    se_slope = np.sqrt(mse / np.sum(X_centered**2))

    t_stat = reg.coef_[0] / se_slope
    p_value_slope = 2 * (1 - stats.t.cdf(abs(t_stat), df_residuals))

    se_intercept = np.sqrt(mse * (1/n + X.mean()**2 / np.sum(X_centered**2)))
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
        'se_intercept': se_intercept,
        't_stat_slope': t_stat,
        't_stat_intercept': t_stat_intercept,
        'df': df_residuals,
        'n': n
    }

# Pooled regression: F1 vs Concreteness
print("\n" + "="*80)
print("POOLED REGRESSION: F1 Score vs Concreteness (All Models)")
print("="*80)

X_pooled = pooled_df['Concreteness'].values.reshape(-1, 1)
y_f1_pooled = pooled_df['F1'].values

stats_f1 = calculate_regression_stats(X_pooled, y_f1_pooled)

print(f"\nEquation: F1 = {stats_f1['slope']:.4f} × Concreteness + {stats_f1['intercept']:.4f}")
print(f"R² = {stats_f1['r_squared']:.4f}  |  n = {stats_f1['n']}  |  df = {stats_f1['df']}")
print()
print(f"{'Parameter':<15} {'Estimate':<12} {'Std Error':<12} {'t-statistic':<12} {'p-value':<12}")
print("-"*80)
print(f"{'Slope (β)':<15} {stats_f1['slope']:>11.4f} {stats_f1['se_slope']:>11.4f} {stats_f1['t_stat_slope']:>11.3f} {stats_f1['p_value_slope']:>11.4f}")
print(f"{'Intercept (α)':<15} {stats_f1['intercept']:>11.4f} {stats_f1['se_intercept']:>11.4f} {stats_f1['t_stat_intercept']:>11.3f} {stats_f1['p_value_intercept']:>11.4f}")

# Interpretation
if stats_f1['p_value_slope'] < 0.001:
    sig_f1 = "highly significant (p < 0.001) ***"
elif stats_f1['p_value_slope'] < 0.01:
    sig_f1 = "very significant (p < 0.01) **"
elif stats_f1['p_value_slope'] < 0.05:
    sig_f1 = "significant (p < 0.05) *"
elif stats_f1['p_value_slope'] < 0.10:
    sig_f1 = "marginally significant (p < 0.10) ."
else:
    sig_f1 = "not significant (p ≥ 0.10)"

print(f"\nInterpretation: The relationship between concreteness and F1 is {sig_f1}")
if stats_f1['slope'] < 0:
    print(f"Direction: NEGATIVE - Higher concreteness predicts LOWER F1 score")
else:
    print(f"Direction: POSITIVE - Higher concreteness predicts HIGHER F1 score")

# Pooled regression: Accuracy vs Concreteness
print("\n" + "="*80)
print("POOLED REGRESSION: Accuracy vs Concreteness (All Models)")
print("="*80)

y_acc_pooled = pooled_df['Accuracy'].values

stats_acc = calculate_regression_stats(X_pooled, y_acc_pooled)

print(f"\nEquation: Accuracy = {stats_acc['slope']:.4f} × Concreteness + {stats_acc['intercept']:.4f}")
print(f"R² = {stats_acc['r_squared']:.4f}  |  n = {stats_acc['n']}  |  df = {stats_acc['df']}")
print()
print(f"{'Parameter':<15} {'Estimate':<12} {'Std Error':<12} {'t-statistic':<12} {'p-value':<12}")
print("-"*80)
print(f"{'Slope (β)':<15} {stats_acc['slope']:>11.4f} {stats_acc['se_slope']:>11.4f} {stats_acc['t_stat_slope']:>11.3f} {stats_acc['p_value_slope']:>11.4f}")
print(f"{'Intercept (α)':<15} {stats_acc['intercept']:>11.4f} {stats_acc['se_intercept']:>11.4f} {stats_acc['t_stat_intercept']:>11.3f} {stats_acc['p_value_intercept']:>11.4f}")

# Interpretation
if stats_acc['p_value_slope'] < 0.001:
    sig_acc = "highly significant (p < 0.001) ***"
elif stats_acc['p_value_slope'] < 0.01:
    sig_acc = "very significant (p < 0.01) **"
elif stats_acc['p_value_slope'] < 0.05:
    sig_acc = "significant (p < 0.05) *"
elif stats_acc['p_value_slope'] < 0.10:
    sig_acc = "marginally significant (p < 0.10) ."
else:
    sig_acc = "not significant (p ≥ 0.10)"

print(f"\nInterpretation: The relationship between concreteness and Accuracy is {sig_acc}")
if stats_acc['slope'] < 0:
    print(f"Direction: NEGATIVE - Higher concreteness predicts LOWER accuracy")
else:
    print(f"Direction: POSITIVE - Higher concreteness predicts HIGHER accuracy")

# Create visualization
print("\n" + "="*80)
print("Creating visualization...")
print("="*80)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Define colors for models
model_colors = {
    'GPT-4': '#1f77b4',
    'GPT-3.5': '#2ca02c',
    'Gemini': '#d62728',
    'Llama': '#7f7f7f'
}

# Plot 1: F1 Score
for model_name in ['GPT-4', 'GPT-3.5', 'Gemini', 'Llama']:
    model_data = pooled_df[pooled_df['Model'] == model_name]
    ax1.scatter(model_data['Concreteness'], model_data['F1'],
                s=120, alpha=0.6, c=model_colors[model_name],
                edgecolors='black', linewidth=1.5, label=model_name)

# Add pooled regression line
x_line = np.linspace(X_pooled.min(), X_pooled.max(), 100).reshape(-1, 1)
y_line_f1 = stats_f1['model'].predict(x_line)

# Format p-value
p_str_f1 = f'p = {stats_f1["p_value_slope"]:.4f}' if stats_f1['p_value_slope'] >= 0.001 else 'p < 0.001'

ax1.plot(x_line, y_line_f1, 'k--', linewidth=3, alpha=0.8,
         label=f'Pooled: y = {stats_f1["slope"]:.3f}x + {stats_f1["intercept"]:.3f}\nR² = {stats_f1["r_squared"]:.3f}, {p_str_f1}')

ax1.set_xlabel('Code Concreteness (Mean)', fontsize=13, fontweight='bold')
ax1.set_ylabel('F1 Score', fontsize=13, fontweight='bold')
ax1.set_title(f'Pooled Regression: F1 Score vs Code Concreteness\nAll Models Combined (n={total_obs})',
             fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=10, framealpha=0.9)
ax1.grid(True, alpha=0.3)

# Plot 2: Accuracy
for model_name in ['GPT-4', 'GPT-3.5', 'Gemini', 'Llama']:
    model_data = pooled_df[pooled_df['Model'] == model_name]
    ax2.scatter(model_data['Concreteness'], model_data['Accuracy'],
                s=120, alpha=0.6, c=model_colors[model_name],
                edgecolors='black', linewidth=1.5, label=model_name)

# Add pooled regression line
y_line_acc = stats_acc['model'].predict(x_line)

# Format p-value
p_str_acc = f'p = {stats_acc["p_value_slope"]:.4f}' if stats_acc['p_value_slope'] >= 0.001 else 'p < 0.001'

ax2.plot(x_line, y_line_acc, 'k--', linewidth=3, alpha=0.8,
         label=f'Pooled: y = {stats_acc["slope"]:.3f}x + {stats_acc["intercept"]:.3f}\nR² = {stats_acc["r_squared"]:.3f}, {p_str_acc}')

ax2.set_xlabel('Code Concreteness (Mean)', fontsize=13, fontweight='bold')
ax2.set_ylabel('Accuracy', fontsize=13, fontweight='bold')
ax2.set_title(f'Pooled Regression: Accuracy vs Code Concreteness\nAll Models Combined (n={total_obs})',
             fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=10, framealpha=0.9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/figures/concreteness_pooled_regression.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/figures/concreteness_pooled_regression.png")

# Correlation analysis
print("\n" + "="*80)
print("CORRELATION ANALYSIS (Pooled Data)")
print("="*80)

corr_f1 = pooled_df['Concreteness'].corr(pooled_df['F1'])
corr_acc = pooled_df['Concreteness'].corr(pooled_df['Accuracy'])

print(f"\nPearson correlation (Concreteness × F1):       r = {corr_f1:.4f}")
print(f"Pearson correlation (Concreteness × Accuracy): r = {corr_acc:.4f}")

# Save pooled data
pooled_df.to_csv('results/outputs/concreteness_pooled_data.csv', index=False)
print(f"\n✓ Saved pooled data: results/outputs/concreteness_pooled_data.csv")

# Summary statistics by model
print("\n" + "="*80)
print("SUMMARY STATISTICS BY MODEL")
print("="*80)

summary_stats = pooled_df.groupby('Model').agg({
    'F1': ['mean', 'std', 'min', 'max'],
    'Accuracy': ['mean', 'std', 'min', 'max']
}).round(3)

print("\n" + str(summary_stats))

# Compare pooled vs individual model regressions
print("\n" + "="*80)
print("COMPARISON: Pooled vs Individual Model Regressions")
print("="*80)

print(f"\n{'Model':<20} {'F1 Slope':<15} {'F1 R²':<15} {'Acc Slope':<15} {'Acc R²':<15}")
print("-"*80)
print(f"{'POOLED (All Models)':<20} {stats_f1['slope']:>14.4f} {stats_f1['r_squared']:>14.4f} {stats_acc['slope']:>14.4f} {stats_acc['r_squared']:>14.4f}")

# Individual models for comparison
for model_name, f1_col, acc_col in models:
    model_data = pooled_df[pooled_df['Model'] == model_name]
    X_model = model_data['Concreteness'].values.reshape(-1, 1)

    y_f1_model = model_data['F1'].values
    stats_f1_model = calculate_regression_stats(X_model, y_f1_model)

    y_acc_model = model_data['Accuracy'].values
    stats_acc_model = calculate_regression_stats(X_model, y_acc_model)

    print(f"{model_name:<20} {stats_f1_model['slope']:>14.4f} {stats_f1_model['r_squared']:>14.4f} {stats_acc_model['slope']:>14.4f} {stats_acc_model['r_squared']:>14.4f}")

print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

print("\n1. POOLED F1 REGRESSION:")
print(f"   - Slope: {stats_f1['slope']:.4f} ({sig_f1})")
print(f"   - R²: {stats_f1['r_squared']:.4f} ({stats_f1['r_squared']*100:.1f}% variance explained)")
print(f"   - With {stats_f1['n']} observations, increased power vs individual models")

print("\n2. POOLED ACCURACY REGRESSION:")
print(f"   - Slope: {stats_acc['slope']:.4f} ({sig_acc})")
print(f"   - R²: {stats_acc['r_squared']:.4f} ({stats_acc['r_squared']*100:.1f}% variance explained)")
print(f"   - Shows {'negative' if stats_acc['slope'] < 0 else 'positive'} relationship")

print("\n3. ADVANTAGE OF POOLING:")
print(f"   - Increases sample size from n={len(results_df_clean)} (per model) to n={total_obs} (pooled)")
print(f"   - Increases degrees of freedom from df={len(results_df_clean) - 2} to df={stats_f1['df']}")
print(f"   - Reduces standard errors (more precise estimates)")
print(f"   - Tests average effect across all models")

print("\n4. INTERPRETATION:")
if stats_f1['p_value_slope'] < 0.05:
    print("   ✓ Strong evidence for concreteness effect on F1 across all models")
else:
    print("   ✗ Insufficient evidence for consistent concreteness effect")

if abs(stats_f1['slope']) > abs(stats_acc['slope']):
    print("   - Concreteness affects F1 (what codes are detected) more than accuracy (precision when detected)")
else:
    print("   - Concreteness affects accuracy more than F1")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
