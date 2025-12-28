"""
Concreteness vs Cohen's Kappa Analysis
Analyzing the relationship between linguistic concreteness and Cohen's Kappa
for GPT-4, GPT-3.5, and Gemini (individual and pooled)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy import stats
import seaborn as sns

# Set style
sns.set_style("whitegrid")

print("="*80)
print("CONCRETENESS vs COHEN'S KAPPA ANALYSIS")
print("="*80)

# Load concreteness data
concreteness_df = pd.read_excel('data/processed/concreteness.xlsx')
concreteness_df['Word'] = concreteness_df['Word'].str.lower()

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
    """Get concreteness score for a text (word or phrase)."""
    words = text.lower().split()
    scores = []
    for word in words:
        if word in ['of', 'the', 'a', 'an']:
            continue
        match = concreteness_df[concreteness_df['Word'] == word]
        if not match.empty:
            scores.append(match.iloc[0]['Conc.M'])
    if scores:
        return np.mean(scores)
    else:
        return np.nan

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

# Get concreteness scores
print("\nCalculating concreteness scores...")
code_concreteness = []
for code in codes:
    score = get_concreteness(code)
    code_concreteness.append({
        'Code': code,
        'Concreteness': score
    })

conc_df = pd.DataFrame(code_concreteness).dropna(subset=['Concreteness'])
print(f"Codes with concreteness scores: {len(conc_df)}/9")

# Load Kappa results
kappa_results = pd.read_csv('results/outputs/intercoder_reliability_results_with_gemini.csv')
kappa_results = kappa_results[kappa_results['Code'] != 'Average']

# Merge with concreteness
results = kappa_results.merge(conc_df, on='Code', how='inner')

# Extract Kappa values for each model
results['Kappa_GPT4'] = results['GPT-4: Per-Code w/ Just']
results['Kappa_GPT35'] = results['GPT-3.5: Per-Code w/ Just']
results['Kappa_Gemini'] = results['Gemini: Per-Code w/ Just']
results['Kappa_Llama'] = results['Llama: Per-Code w/ Just']

print(f"\nFinal dataset: {len(results)} codes")

# Create long-format dataset for pooled analysis
data_long = []
for _, row in results.iterrows():
    code = row['Code']
    conc = row['Concreteness']
    data_long.append({'Code': code, 'Model': 'GPT-4', 'Concreteness': conc, 'Kappa': row['Kappa_GPT4']})
    data_long.append({'Code': code, 'Model': 'GPT-3.5', 'Concreteness': conc, 'Kappa': row['Kappa_GPT35']})
    data_long.append({'Code': code, 'Model': 'Gemini', 'Concreteness': conc, 'Kappa': row['Kappa_Gemini']})
    data_long.append({'Code': code, 'Model': 'Llama', 'Concreteness': conc, 'Kappa': row['Kappa_Llama']})

pooled_df = pd.DataFrame(data_long)
pooled_n = len(pooled_df)

# Save data
results.to_csv('results/outputs/concreteness_kappa_analysis.csv', index=False)
pooled_df.to_csv('results/outputs/concreteness_kappa_pooled.csv', index=False)
print("✓ Saved: results/outputs/concreteness_kappa_analysis.csv")
print("✓ Saved: results/outputs/concreteness_kappa_pooled.csv")

# Run regressions for each model
print("\n" + "="*80)
print("INDIVIDUAL MODEL REGRESSIONS")
print("="*80)

X = results['Concreteness'].values.reshape(-1, 1)

models = [
    ('GPT-4', 'Kappa_GPT4', '#1f77b4'),
    ('GPT-3.5', 'Kappa_GPT35', '#2ca02c'),
    ('Gemini', 'Kappa_Gemini', '#d62728'),
    ('Llama', 'Kappa_Llama', '#7f7f7f')
]

individual_stats = {}

for model_name, kappa_col, color in models:
    y = results[kappa_col].values
    stats_dict = calculate_regression_stats(X, y)
    individual_stats[model_name] = stats_dict

    print(f"\n--- {model_name} ---")
    print(f"Equation: κ = {stats_dict['slope']:.4f} × Concreteness + {stats_dict['intercept']:.4f}")
    print(f"R² = {stats_dict['r_squared']:.4f}  |  n = {stats_dict['n']}  |  df = {stats_dict['df']}")
    print(f"Slope: β = {stats_dict['slope']:.4f}, SE = {stats_dict['se_slope']:.4f}, t = {stats_dict['t_stat_slope']:.3f}, p = {stats_dict['p_value_slope']:.4f}")

    # Significance
    if stats_dict['p_value_slope'] < 0.001:
        sig = "***"
    elif stats_dict['p_value_slope'] < 0.01:
        sig = "**"
    elif stats_dict['p_value_slope'] < 0.05:
        sig = "*"
    elif stats_dict['p_value_slope'] < 0.10:
        sig = "."
    else:
        sig = "ns"

    print(f"Significance: {sig}")
    print(f"Correlation: r = {results['Concreteness'].corr(results[kappa_col]):.4f}")

# Pooled regression
print("\n" + "="*80)
print("POOLED REGRESSION (All Models Combined)")
print("="*80)

X_pooled = pooled_df['Concreteness'].values.reshape(-1, 1)
y_pooled = pooled_df['Kappa'].values

pooled_stats = calculate_regression_stats(X_pooled, y_pooled)

print(f"\nEquation: κ = {pooled_stats['slope']:.4f} × Concreteness + {pooled_stats['intercept']:.4f}")
print(f"R² = {pooled_stats['r_squared']:.4f}  |  n = {pooled_stats['n']}  |  df = {pooled_stats['df']}")
print(f"Slope: β = {pooled_stats['slope']:.4f}, SE = {pooled_stats['se_slope']:.4f}, t = {pooled_stats['t_stat_slope']:.3f}, p = {pooled_stats['p_value_slope']:.4f}")

if pooled_stats['p_value_slope'] < 0.001:
    sig_pooled = "***"
elif pooled_stats['p_value_slope'] < 0.01:
    sig_pooled = "**"
elif pooled_stats['p_value_slope'] < 0.05:
    sig_pooled = "*"
elif pooled_stats['p_value_slope'] < 0.10:
    sig_pooled = "."
else:
    sig_pooled = "ns"

print(f"Significance: {sig_pooled}")
print(f"Correlation: r = {pooled_df['Concreteness'].corr(pooled_df['Kappa']):.4f}")

# Create visualization
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

# Figure 1: Individual model regressions (2x3 grid with pooled)
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

plot_configs = [
    ('GPT-4', 'Kappa_GPT4', '#1f77b4', individual_stats['GPT-4']),
    ('GPT-3.5', 'Kappa_GPT35', '#2ca02c', individual_stats['GPT-3.5']),
    ('Gemini', 'Kappa_Gemini', '#d62728', individual_stats['Gemini']),
    ('Llama', 'Kappa_Llama', '#7f7f7f', individual_stats['Llama']),
    ('Pooled (All Models)', None, 'multi', pooled_stats)
]

for idx, (model_name, kappa_col, color, stats_dict) in enumerate(plot_configs):
    ax = axes[idx]

    if model_name == 'Pooled (All Models)':
        # Pooled plot with all models shown
        for m_name, m_col, m_color in models:
            model_data = pooled_df[pooled_df['Model'] == m_name]
            ax.scatter(model_data['Concreteness'], model_data['Kappa'],
                      s=120, alpha=0.6, c=m_color, edgecolors='black',
                      linewidth=1.5, label=m_name)

        # Pooled regression line
        x_line = np.linspace(X_pooled.min(), X_pooled.max(), 100).reshape(-1, 1)
        y_line = stats_dict['model'].predict(x_line)
        p_str = f'p = {stats_dict["p_value_slope"]:.4f}' if stats_dict['p_value_slope'] >= 0.001 else 'p < 0.001'

        ax.plot(x_line, y_line, 'k--', linewidth=3, alpha=0.8,
               label=f'Pooled: y = {stats_dict["slope"]:.3f}x + {stats_dict["intercept"]:.3f}\nR² = {stats_dict["r_squared"]:.3f}, {p_str}')
        ax.legend(loc='best', fontsize=9)
    else:
        # Individual model plot
        ax.scatter(results['Concreteness'], results[kappa_col],
                  s=150, alpha=0.6, c=color, edgecolors='black', linewidth=1.5)

        # Add code labels
        for _, row in results.iterrows():
            ax.annotate(row['Code'], (row['Concreteness'], row[kappa_col]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=7, alpha=0.7)

        # Regression line
        x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_line = stats_dict['model'].predict(x_line)
        p_str = f'p = {stats_dict["p_value_slope"]:.4f}' if stats_dict['p_value_slope'] >= 0.001 else 'p < 0.001'

        ax.plot(x_line, y_line, 'r--', linewidth=2, alpha=0.8,
               label=f'y = {stats_dict["slope"]:.3f}x + {stats_dict["intercept"]:.3f}\nR² = {stats_dict["r_squared"]:.3f}, {p_str}')
        ax.legend(loc='best', fontsize=9)

    ax.set_xlabel('Code Concreteness (Mean)', fontsize=11, fontweight='bold')
    ax.set_ylabel("Cohen's Kappa (κ)", fontsize=11, fontweight='bold')
    ax.set_title(f'{model_name}: Kappa vs Concreteness\n(n={stats_dict["n"]})',
                fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

# Hide any unused axes
for ax in axes[len(plot_configs):]:
    ax.axis('off')

plt.tight_layout()
plt.savefig('results/figures/concreteness_vs_kappa_all_models.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/figures/concreteness_vs_kappa_all_models.png")

# Figure 2: Comparison plot (all models on one plot)
fig, ax = plt.subplots(figsize=(12, 8))

for model_name, kappa_col, color in models:
    ax.scatter(results['Concreteness'], results[kappa_col],
              s=200, alpha=0.7, c=color, edgecolors='black',
              linewidth=2, label=model_name, marker='o')

    # Individual regression lines
    stats_dict = individual_stats[model_name]
    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = stats_dict['model'].predict(x_line)
    ax.plot(x_line, y_line, color=color, linestyle='--', linewidth=2, alpha=0.6)

# Add pooled regression line
x_line_pooled = np.linspace(X_pooled.min(), X_pooled.max(), 100).reshape(-1, 1)
y_line_pooled = pooled_stats['model'].predict(x_line_pooled)
p_str_pooled = f'p = {pooled_stats["p_value_slope"]:.4f}' if pooled_stats['p_value_slope'] >= 0.001 else 'p < 0.001'

ax.plot(x_line_pooled, y_line_pooled, 'k-', linewidth=3, alpha=0.8,
       label=f'Pooled: β = {pooled_stats["slope"]:.3f}, R² = {pooled_stats["r_squared"]:.3f}, {p_str_pooled}')

ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5, zorder=0)
ax.set_xlabel('Code Concreteness (Mean)', fontsize=13, fontweight='bold')
ax.set_ylabel("Cohen's Kappa (κ)", fontsize=13, fontweight='bold')
ax.set_title("Model Performance vs Code Concreteness\nComparing GPT-4, GPT-3.5, Gemini, and Llama",
            fontsize=15, fontweight='bold')
ax.legend(loc='best', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/figures/concreteness_vs_kappa_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: results/figures/concreteness_vs_kappa_comparison.png")

# Summary statistics table
print("\n" + "="*80)
print("SUMMARY TABLE: Concreteness vs Kappa Regressions")
print("="*80)

print(f"\n{'Model':<20} {'Slope (β)':<15} {'p-value':<12} {'R²':<10} {'Corr (r)':<12} {'Sig':<5}")
print("-"*80)

for model_name, kappa_col, _ in models:
    stats_dict = individual_stats[model_name]
    corr = results['Concreteness'].corr(results[kappa_col])

    if stats_dict['p_value_slope'] < 0.001:
        sig = "***"
    elif stats_dict['p_value_slope'] < 0.01:
        sig = "**"
    elif stats_dict['p_value_slope'] < 0.05:
        sig = "*"
    elif stats_dict['p_value_slope'] < 0.10:
        sig = "."
    else:
        sig = "ns"

    print(f"{model_name:<20} {stats_dict['slope']:>14.4f} {stats_dict['p_value_slope']:>11.4f} {stats_dict['r_squared']:>9.4f} {corr:>11.4f} {sig:>5}")

# Pooled
corr_pooled = pooled_df['Concreteness'].corr(pooled_df['Kappa'])
print(f"{'POOLED (n=' + str(pooled_n) + ')':<20} {pooled_stats['slope']:>14.4f} {pooled_stats['p_value_slope']:>11.4f} {pooled_stats['r_squared']:>9.4f} {corr_pooled:>11.4f} {sig_pooled:>5}")

print("\nSignificance codes: *** p<0.001  ** p<0.01  * p<0.05  . p<0.10  ns = not significant")

# Key findings
print("\n" + "="*80)
print("KEY FINDINGS")
print("="*80)

print("\n1. INDIVIDUAL MODEL PATTERNS:")
for model_name, kappa_col, _ in models:
    stats_dict = individual_stats[model_name]
    if stats_dict['p_value_slope'] < 0.05:
        print(f"   ✓ {model_name}: Significant relationship (p = {stats_dict['p_value_slope']:.4f})")
    else:
        print(f"   ✗ {model_name}: No significant relationship (p = {stats_dict['p_value_slope']:.4f})")

print("\n2. POOLED ANALYSIS:")
if pooled_stats['p_value_slope'] < 0.05:
    print(f"   ✓ Significant effect across all models (p = {pooled_stats['p_value_slope']:.4f})")
else:
    print(f"   ✗ No significant effect when pooled (p = {pooled_stats['p_value_slope']:.4f})")

print("\n3. COMPARISON WITH F1/ACCURACY ANALYSES:")
print("   - F1 and Kappa measure different aspects of agreement")
print("   - F1 focuses on positive class (when code is applied)")
print("   - Kappa accounts for both positive and negative agreement")
print("   - Check if patterns are consistent across metrics")

print("\n4. INTERPRETATION:")
if individual_stats['GPT-4']['p_value_slope'] < 0.05:
    print(f"   - GPT-4 shows concreteness effect on Kappa (β = {individual_stats['GPT-4']['slope']:.4f})")
else:
    print("   - GPT-4 does NOT show significant concreteness effect on Kappa")

if pooled_stats['slope'] < 0:
    print(f"   - Overall trend: Higher concreteness → Lower Kappa")
else:
    print(f"   - Overall trend: Higher concreteness → Higher Kappa")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
