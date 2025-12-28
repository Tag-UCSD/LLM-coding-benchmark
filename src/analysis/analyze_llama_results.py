"""
Analyze Llama results: Calculate intercoder reliability metrics
Compare Llama to gold standard and GPT-4
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


def analyze_llama_vs_gold_standard():
    """Compare Llama coding to gold standard."""

    print("\n" + "=" * 80)
    print("LLAMA VS GOLD STANDARD COMPARISON")
    print("=" * 80)

    gold_standard_path = 'data/processed/gold_standard_coding.csv'
    llama_with_just_path = 'results/raw/output_llama/per-code-with-justification_t=0_model=llama-3.3-70b/processed_responses.csv'

    print("\n--- Llama 3.1 70B (per-code with justification) ---")
    results = get_ir_report_df(
        [gold_standard_path, llama_with_just_path],
        CODED_COLUMNS,
        ids=range(9, 120),
        id_column='id'
    )

    print(results.to_string(index=False))
    print(f"\nAverage Cohen's Kappa: {results['Kappa'].mean():.3f}")
    print(f"Average Percent Agreement: {results['% Agreement'].mean():.3f}")

    # Save results
    results.to_csv('results/outputs/llama_vs_gold_standard.csv', index=False)
    print(f"\n✓ Saved to: results/outputs/llama_vs_gold_standard.csv")

    return results


def compare_llama_to_gpt4():
    """Compare Llama performance to GPT-4."""

    print("\n" + "=" * 80)
    print("LLAMA VS GPT-4 COMPARISON")
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

    # Load Llama results
    llama_results = pd.read_csv('results/outputs/llama_vs_gold_standard.csv')

    # Compare
    comparison = pd.DataFrame({
        'Code': gpt4_results['Code'].values,
        'GPT-4 Kappa': gpt4_results['Kappa'].values,
        'Llama Kappa': llama_results['Kappa'].values,
        'Difference': llama_results['Kappa'].values - gpt4_results['Kappa'].values,
        'GPT-4 % Agreement': gpt4_results['% Agreement'].values,
        'Llama % Agreement': llama_results['% Agreement'].values,
    })

    print("\n" + comparison.to_string(index=False))
    print(f"\nAverage Kappa - GPT-4: {comparison['GPT-4 Kappa'].mean():.3f}")
    print(f"Average Kappa - Llama: {comparison['Llama Kappa'].mean():.3f}")
    print(f"Difference: {comparison['Difference'].mean():.3f}")

    # Save
    comparison.to_csv('results/outputs/llama_vs_gpt4_comparison.csv', index=False)
    print(f"\n✓ Saved to: results/outputs/llama_vs_gpt4_comparison.csv")

    return comparison


if __name__ == "__main__":
    # Analyze Llama results
    llama_results = analyze_llama_vs_gold_standard()

    # Compare to GPT-4
    comparison = compare_llama_to_gpt4()
