"""
Analyze relationship between code concreteness and LLM performance
Updated to include Gemini alongside GPT models
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
plt.rcParams['figure.figsize'] = (16, 10)

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

    # Fill NaN with 0 (code not applied)
    merged = merged.fillna(0)

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

# Load gold standard and model predictions
print("\nLoading model results...")
gold_standard = pd.read_csv('data/processed/gold_standard_coding.csv')
gpt4 = pd.read_csv('results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv')
gpt35 = pd.read_csv('results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-3.5/processed_responses.csv')
gemini_per = pd.read_csv('results/raw/output_gemini/per-code-with-justification_t=0_top_p=1_model=gemini/processed_responses.csv')
llama_per = pd.read_csv('results/raw/output_llama/per-code-with-justification_t=0_model=llama-3.3-70b/processed_responses.csv')

# Calculate F1 and accuracy for each code and model
print("\nCalculating performance metrics...")
results = []
for code in codes:
    conc = concreteness_df[concreteness_df['code'] == code]['concreteness'].values[0]

    # GPT-4
    f1_gpt4, acc_gpt4 = calculate_f1_and_accuracy(gold_standard, gpt4, code)

    # GPT-3.5
    f1_gpt35, acc_gpt35 = calculate_f1_and_accuracy(gold_standard, gpt35, code)

    # Gemini
    f1_gemini, acc_gemini = calculate_f1_and_accuracy(gold_standard, gemini_per, code)

    # Llama
    f1_llama, acc_llama = calculate_f1_and_accuracy(gold_standard, llama_per, code)

    results.append({
        'Code': code,
        'Concreteness': conc,
        'F1_GPT4': f1_gpt4,
        'Acc_GPT4': acc_gpt4,
        'F1_GPT35': f1_gpt35,
        'Acc_GPT35': acc_gpt35,
        'F1_Gemini': f1_gemini,
        'Acc_Gemini': acc_gemini,
        'F1_Llama': f1_llama,
        'Acc_Llama': acc_llama
    })
    print(f"  {code}:")
    print(f"    GPT-4: F1={f1_gpt4:.3f}, Acc={acc_gpt4:.3f}")
    print(f"    GPT-3.5: F1={f1_gpt35:.3f}, Acc={acc_gpt35:.3f}")
    print(f"    Gemini: F1={f1_gemini:.3f}, Acc={acc_gemini:.3f}")
    print(f"    Llama: F1={f1_llama:.3f}, Acc={acc_llama:.3f}")
    print(f"    Concreteness: {conc:.2f}" if not np.isnan(conc) else "    Concreteness: N/A")

results_df = pd.DataFrame(results)

# Remove any codes with missing concreteness scores
results_df_clean = results_df.dropna(subset=['Concreteness'])

print(f"\n{len(results_df_clean)} out of {len(results_df)} codes have concreteness scores")

# Save results
results_df.to_csv('results/outputs/code_concreteness_analysis_with_gemini.csv', index=False)
print("\n✓ Saved analysis to results/outputs/code_concreteness_analysis_with_gemini.csv")

# Create visualization with all four models
fig, axes = plt.subplots(2, 4, figsize=(22, 12))
axes = axes.flatten()

models = [
    ('GPT-4', 'F1_GPT4', 'Acc_GPT4', 'steelblue'),
    ('GPT-3.5', 'F1_GPT35', 'Acc_GPT35', 'darkgreen'),
    ('Gemini', 'F1_Gemini', 'Acc_Gemini', 'darkorange'),
    ('Llama', 'F1_Llama', 'Acc_Llama', '#7f7f7f')
]

for idx, (model_name, f1_col, acc_col, color) in enumerate(models):
    # F1 Score plot
    ax_f1 = axes[idx]
    ax_acc = axes[idx + len(models)]

    if len(results_df_clean) > 1:
        X = results_df_clean['Concreteness'].values.reshape(-1, 1)
        y_f1 = results_df_clean[f1_col].values
        y_acc = results_df_clean[acc_col].values

        # F1 regression
        reg_stats_f1 = calculate_regression_stats(X, y_f1)
        x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_line_f1 = reg_stats_f1['model'].predict(x_line)

        # F1 scatter
        ax_f1.scatter(results_df_clean['Concreteness'], y_f1,
                    s=150, alpha=0.6, c=color, edgecolors='black', linewidth=1.5)

        # Format p-value
        p_slope_f1 = reg_stats_f1['p_value_slope']
        p_str_f1 = f'p = {p_slope_f1:.3f}' if p_slope_f1 >= 0.001 else 'p < 0.001'

        # Plot regression line
        ax_f1.plot(x_line, y_line_f1, 'r--', linewidth=2, alpha=0.8,
                 label=f'y = {reg_stats_f1["slope"]:.3f}x + {reg_stats_f1["intercept"]:.3f}\nR² = {reg_stats_f1["r_squared"]:.3f}, {p_str_f1}')

        ax_f1.set_xlabel('Code Concreteness (Mean)', fontsize=11, fontweight='bold')
        ax_f1.set_ylabel('F1 Score', fontsize=11, fontweight='bold')
        ax_f1.set_title(f'{model_name} Performance vs Code Concreteness\n(F1 Score)',
                     fontsize=12, fontweight='bold')
        ax_f1.legend(loc='best', fontsize=9)
        ax_f1.grid(True, alpha=0.3)

        # Accuracy regression
        reg_stats_acc = calculate_regression_stats(X, y_acc)
        y_line_acc = reg_stats_acc['model'].predict(x_line)

        # Accuracy scatter
        ax_acc.scatter(results_df_clean['Concreteness'], y_acc,
                    s=150, alpha=0.6, c=color, edgecolors='black', linewidth=1.5)

        # Format p-value
        p_slope_acc = reg_stats_acc['p_value_slope']
        p_str_acc = f'p = {p_slope_acc:.3f}' if p_slope_acc >= 0.001 else 'p < 0.001'

        # Plot regression line
        ax_acc.plot(x_line, y_line_acc, 'r--', linewidth=2, alpha=0.8,
                 label=f'y = {reg_stats_acc["slope"]:.3f}x + {reg_stats_acc["intercept"]:.3f}\nR² = {reg_stats_acc["r_squared"]:.3f}, {p_str_acc}')

        ax_acc.set_xlabel('Code Concreteness (Mean)', fontsize=11, fontweight='bold')
        ax_acc.set_ylabel('Accuracy', fontsize=11, fontweight='bold')
        ax_acc.set_title(f'{model_name} Performance vs Code Concreteness\n(Accuracy)',
                     fontsize=12, fontweight='bold')
        ax_acc.legend(loc='best', fontsize=9)
        ax_acc.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/figures/concreteness_vs_performance_with_gemini.png', dpi=300, bbox_inches='tight')
print("✓ Saved visualization to results/figures/concreteness_vs_performance_with_gemini.png")

# Print summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)

for model_name, f1_col, acc_col, _ in models:
    print(f"\n--- {model_name} ---")
    print(f"Correlation between Concreteness and F1: {results_df_clean['Concreteness'].corr(results_df_clean[f1_col]):.3f}")
    print(f"Correlation between Concreteness and Accuracy: {results_df_clean['Concreteness'].corr(results_df_clean[acc_col]):.3f}")
    print(f"Mean F1: {results_df_clean[f1_col].mean():.3f} (SD: {results_df_clean[f1_col].std():.3f})")
    print(f"Mean Accuracy: {results_df_clean[acc_col].mean():.3f} (SD: {results_df_clean[acc_col].std():.3f})")

print("\n" + "="*80)
print("DONE")
print("="*80)
