"""
Analyze Qwen results: Calculate intercoder reliability metrics
Compare Qwen to gold standard and GPT-4
"""

import pandas as pd
import sys

# Import functions from replicate_analysis.py
from replicate_analysis import get_ir_report_df

CODED_COLUMNS = [
    'Scholar', 'Activist', 'Monumental Memorialization',
    'Mention of Scholarly Work', 'Social/Political Advocacy',
    'Coalition Building', 'Out of the Mouth of Academics',
    'Out of the Mouth of Activists', 'Collective Synecdoche'
]


def analyze_qwen_vs_gold_standard():
    """Compare Qwen coding to gold standard."""

    print("\n" + "=" * 80)
    print("QWEN VS GOLD STANDARD COMPARISON")
    print("=" * 80)

    gold_standard_path = 'data/processed/gold_standard_coding.csv'
    qwen_with_just_path = 'results/raw/output_qwen/per-code-with-justification_t=0_model=qwen-2.5-72b/processed_responses.csv'

    print("\n--- Qwen 2.5 72B (per-code with justification) ---")
    results = get_ir_report_df(
        [gold_standard_path, qwen_with_just_path],
        CODED_COLUMNS,
        ids=range(9, 120),
        id_column='id'
    )

    print(results.to_string(index=False))
    print(f"\nAverage Cohen's Kappa: {results['Kappa'].mean():.3f}")
    print(f"Average Percent Agreement: {results['% Agreement'].mean():.3f}")

    # Save results
    results.to_csv('results/outputs/qwen_vs_gold_standard.csv', index=False)
    print(f"\n✓ Saved to: results/outputs/qwen_vs_gold_standard.csv")

    return results


def compare_qwen_to_gpt4():
    """Compare Qwen performance to GPT-4."""

    print("\n" + "=" * 80)
    print("QWEN VS GPT-4 COMPARISON")
    print("=" * 80)

    gold_standard_path = 'data/processed/gold_standard_coding.csv'
    gpt4_path = 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv'

    # Freshly compute GPT-4 results to match structure
    gpt4_results = get_ir_report_df(
        [gold_standard_path, gpt4_path],
        CODED_COLUMNS,
        ids=range(9, 120),
        id_column='id'
    )

    # Load Qwen results
    qwen_results = pd.read_csv('results/outputs/qwen_vs_gold_standard.csv')

    # Compare
    comparison = pd.DataFrame({
        'Code': gpt4_results['Code'].values,
        'GPT-4 Kappa': gpt4_results['Kappa'].values,
        'Qwen Kappa': qwen_results['Kappa'].values,
        'Difference': qwen_results['Kappa'].values - gpt4_results['Kappa'].values,
        'GPT-4 % Agreement': gpt4_results['% Agreement'].values,
        'Qwen % Agreement': qwen_results['% Agreement'].values,
    })

    print("\n" + comparison.to_string(index=False))
    print(f"\nAverage Kappa - GPT-4: {comparison['GPT-4 Kappa'].mean():.3f}")
    print(f"Average Kappa - Qwen: {comparison['Qwen Kappa'].mean():.3f}")
    print(f"Difference: {comparison['Difference'].mean():.3f}")

    # Save
    comparison.to_csv('results/outputs/qwen_vs_gpt4_comparison.csv', index=False)
    print(f"\n✓ Saved to: results/outputs/qwen_vs_gpt4_comparison.csv")

    return comparison


if __name__ == "__main__":
    # Analyze Qwen results
    qwen_results = analyze_qwen_vs_gold_standard()

    # Compare to GPT-4
    comparison = compare_qwen_to_gpt4()
