"""
Analyze Gemini coding results and compare with GPT
"""

import pandas as pd
import numpy as np
import os
from sklearn.metrics import cohen_kappa_score
import krippendorff
from pycm import ConfusionMatrix

# Reuse the analysis functions from replicate_analysis.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
from replicate_analysis import (
    load_and_align_data,
    calculate_intercoder_reliability,
    calculate_differential_count,
    get_ir_report_df
)

# Code names
coded_columns = ['Scholar', 'Activist',
                 'Monumental Memorialization', 'Mention of Scholarly Work',
                 'Social/Political Advocacy', 'Coalition Building',
                 'Out of the Mouth of Academics', 'Out of the Mouth of Activists',
                 'Collective Synecdoche']

# Test set IDs
row_ids = range(9, 120)


def analyze_gemini_vs_gold_standard():
    """Compare Gemini outputs against gold standard."""

    print("=" * 80)
    print("GEMINI vs GOLD STANDARD ANALYSIS")
    print("=" * 80)

    # Find all Gemini processed outputs
    base_dir = 'results/raw/output_gemini'

    if not os.path.exists(base_dir):
        print(f"No Gemini outputs found at {base_dir}")
        return None

    results = {}

    for condition_dir in os.listdir(base_dir):
        condition_path = os.path.join(base_dir, condition_dir)

        if not os.path.isdir(condition_path):
            continue

        processed_file = os.path.join(condition_path, 'processed_responses.csv')

        if not os.path.exists(processed_file):
            continue

        print(f"\nAnalyzing: {condition_dir}")

        try:
            pair = ['data/processed/gold_standard_coding.csv', processed_file]
            report_df = get_ir_report_df(pair, coded_columns, ids=row_ids, id_column='id')

            # Extract condition name
            condition_name = condition_dir.replace('results/raw/output_gemini/', '')
            results[condition_name] = report_df

            # Save detailed report
            detail_file = os.path.join(condition_path, 'detailed_report.csv')
            report_df.to_csv(detail_file, index=False)
            print(f"  ✓ Saved: {detail_file}")

            # Print summary
            avg_kappa = report_df['Kappa'].mean()
            print(f"  Average Kappa: {avg_kappa:.3f}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    return results


def compare_gemini_vs_gpt():
    """Compare Gemini and GPT performance."""

    print("\n" + "=" * 80)
    print("GEMINI vs GPT COMPARISON")
    print("=" * 80)

    # Prepare comparison data
    comparison_data = {'Code': coded_columns}

    # Add GPT results
    gpt_conditions = {
        'GPT-4 Per-Code w/ Just': 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4',
        'GPT-4 Per-Code w/o Just': 'results/raw/output_original/per-code-without-justification_t=0_top_p=1_model=gpt-4',
        'GPT-4 Full w/ Just': 'results/raw/output_original/full-codebook_with_justification_t=0_top_p=1_model=gpt-4',
        'GPT-4 Full w/o Just': 'results/raw/output_original/full-codebook_without_justification_t=0_top_p=1_model=gpt-4',
    }

    for name, path in gpt_conditions.items():
        processed_file = f'{path}/processed_responses.csv'
        if os.path.exists(processed_file):
            try:
                pair = ['data/processed/gold_standard_coding.csv', processed_file]
                report_df = get_ir_report_df(pair, coded_columns, ids=row_ids, id_column='id')
                comparison_data[name] = report_df['Kappa'].values
            except Exception as e:
                print(f"  Error loading {name}: {str(e)}")

    # Add Gemini results
    gemini_base = 'results/raw/output_gemini'
    if os.path.exists(gemini_base):
        for condition_dir in os.listdir(gemini_base):
            condition_path = os.path.join(gemini_base, condition_dir)
            processed_file = os.path.join(condition_path, 'processed_responses.csv')

            if os.path.exists(processed_file):
                try:
                    pair = ['data/processed/gold_standard_coding.csv', processed_file]
                    report_df = get_ir_report_df(pair, coded_columns, ids=row_ids, id_column='id')

                    # Clean up name
                    name = condition_dir.replace('_t=0_top_p=1_model=gemini', '')
                    name = 'Gemini ' + name.replace('-', ' ').title()
                    comparison_data[name] = report_df['Kappa'].values
                except Exception as e:
                    print(f"  Error loading {condition_dir}: {str(e)}")

    # Create comparison DataFrame
    df = pd.DataFrame(comparison_data)

    # Add average row
    numeric_columns = df.select_dtypes(include=['number']).columns
    average_row = df[numeric_columns].mean().to_frame().T
    average_row['Code'] = 'Average'
    df = pd.concat([df, average_row], ignore_index=True)

    return df


def main():
    """Main analysis function."""

    # Analyze Gemini vs Gold Standard
    gemini_results = analyze_gemini_vs_gold_standard()

    # Compare Gemini vs GPT
    comparison_df = compare_gemini_vs_gpt()

    if comparison_df is not None:
        print("\n" + "=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)
        print("\n" + comparison_df.to_string(index=False))

        # Save comparison
        output_file = 'results/outputs/gemini_vs_gpt_comparison.csv'
        comparison_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved comparison to: {output_file}")

    return comparison_df


if __name__ == "__main__":
    results = main()
