"""
Replication script for "Scalable Qualitative Coding with LLMs"
Calculates intercoder reliability metrics comparing GPT coding to gold standard
"""

import pandas as pd
import numpy as np
import os
from sklearn.metrics import cohen_kappa_score
import krippendorff
from pycm import ConfusionMatrix

# Code names from the study
coded_columns = ['Scholar', 'Activist',
         'Monumental Memorialization', 'Mention of Scholarly Work',
         'Social/Political Advocacy', 'Coalition Building',
         'Out of the Mouth of Academics', 'Out of the Mouth of Activists',
         'Collective Synecdoche']

# IDs of passages in test set
row_ids = range(9, 120)


def load_and_align_data(files, ids, id_column=None):
    """
    Load data from multiple files and align them based on the specified id column or index.
    Only include rows where the id is in the provided ids list.
    """
    data_frames = []
    for file in files:
        df = pd.read_csv(file)

        # If id_column is not specified or doesn't exist, create it from the index
        if not id_column or id_column not in df.columns:
            df['id'] = df.index
            id_column = 'id'

        # Filter the DataFrame based on the id_column
        df = df[df[id_column].isin(ids)]

        # Replace empty cells with 0
        df.fillna(0, inplace=True)
        df.set_index(id_column, inplace=True)
        df.index = df.index.astype(str)
        data_frames.append(df)

    # Align dataframes
    aligned_df = pd.concat(data_frames, axis=1, keys=range(len(data_frames)))

    return aligned_df


def calculate_cohens_kappa(df, columns):
    """Calculate Cohen's Kappa for each pair of coders for each column."""
    n = len(df.columns.levels[0])
    kappa_scores = {}

    for col in columns:
        scores = []
        for i in range(n):
            for j in range(i+1, n):
                kappa = cohen_kappa_score(df[i][col], df[j][col])
                scores.append((f'Coder {i+1} vs Coder {j+1}', kappa))
        kappa_scores[col] = scores

    return kappa_scores


def calculate_krippendorffs_alpha(df, columns):
    """Calculate Krippendorff's Alpha for each column."""
    alpha_scores = {}
    for col in columns:
        reliability_data = np.array([df[coder][col] for coder in df.columns.levels[0]])
        alpha = krippendorff.alpha(reliability_data)
        alpha_scores[col] = alpha
    return alpha_scores


def calculate_gwets_ac1(df, columns):
    """Calculate Gwet's AC1 for each pair of coders for each column."""
    n = len(df.columns.levels[0])
    gwets_ac1_scores = {}

    for col in columns:
        scores = []
        for i in range(n):
            for j in range(i+1, n):
                coder_i_series = df[i][col].reset_index(drop=True)
                coder_j_series = df[j][col].reset_index(drop=True)

                # Convert series to numpy arrays
                coder_i_ratings = coder_i_series.to_numpy().astype(np.int32)
                coder_j_ratings = coder_j_series.to_numpy().astype(np.int32)

                # Create the confusion matrix
                cm = ConfusionMatrix(coder_i_ratings, coder_j_ratings)

                ac1 = cm.AC1
                scores.append((f'Coder {i+1} vs Coder {j+1}', ac1))
        gwets_ac1_scores[col] = scores

    return gwets_ac1_scores


def calculate_percent_agreement(df, columns):
    """Calculate percent agreement for each pair of coders for each column."""
    n = len(df.columns.levels[0])
    percent_agreement_scores = {}

    for col in columns:
        scores = []
        for i in range(n):
            for j in range(i+1, n):
                agreement = np.mean(df[i][col] == df[j][col])
                scores.append((f'Coder {i+1} vs Coder {j+1}', agreement))
        percent_agreement_scores[col] = scores

    return percent_agreement_scores


def calculate_intercoder_reliability(aligned_df, coded_columns):
    """Calculate all intercoder reliability metrics."""
    kappa_scores = calculate_cohens_kappa(aligned_df, coded_columns)
    alpha_scores = calculate_krippendorffs_alpha(aligned_df, coded_columns)
    percent_agreement_scores = calculate_percent_agreement(aligned_df, coded_columns)
    gwets_ac1_scores = calculate_gwets_ac1(aligned_df, coded_columns)

    return kappa_scores, alpha_scores, percent_agreement_scores, gwets_ac1_scores


def calculate_differential_count(df, coder1, coder2, codes):
    """
    Calculate the sum of applications for each code by two coders and the difference between these sums.
    """
    differential_data = []

    for code in codes:
        coder1_sum = df[coder1][code].sum()
        coder2_sum = df[coder2][code].sum()
        diff = abs(coder1_sum - coder2_sum)

        differential_data.append({
            'Code': code,
            'Coder 1': coder1_sum,
            'Coder 2': coder2_sum,
            'Difference': diff
        })

    return pd.DataFrame(differential_data)


def get_ir_report_df(coding_pair, coded_columns, ids=None, id_column=None):
    """Generate intercoder reliability report DataFrame."""
    aligned_df = load_and_align_data(coding_pair, ids=ids, id_column=id_column)

    results_df = calculate_differential_count(aligned_df, 0, 1, codes=coded_columns)

    kappa_scores, alpha_scores, percent_agreement_scores, gwets_ac1_scores = calculate_intercoder_reliability(aligned_df, coded_columns)

    results_df['% Agreement'] = [v[0][1] for v in percent_agreement_scores.values()]
    results_df['Kappa'] = [v[0][1] for v in kappa_scores.values()]
    results_df['Alpha'] = alpha_scores.values()
    results_df['Gwets AC1'] = [v[0][1] for v in gwets_ac1_scores.values()]

    return results_df


def gold_standard_vs_gpt_comparison():
    """Compare all GPT conditions against gold standard."""

    dirs = {
        'Per Code w/ Justification': 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4',
        'Per Code w/out Justification': 'results/raw/output_original/per-code-without-justification_t=0_top_p=1_model=gpt-4',
        'Full w/ Justification': 'results/raw/output_original/full-codebook_with_justification_t=0_top_p=1_model=gpt-4',
        'Full w/out Justification': 'results/raw/output_original/full-codebook_without_justification_t=0_top_p=1_model=gpt-4',
        'GPT 3.5 w/ Justification': 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-3.5',
        'GPT 3.5 w/out Justification': 'results/raw/output_original/per-code-without-justification_t=0_top_p=1_model=gpt-3.5',
    }

    all_code_comparison = {}

    for k, dir_path in dirs.items():
        file_path = f'{dir_path}/processed_responses.csv'

        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found, skipping...")
            continue

        pair = ['data/processed/gold_standard_coding.csv', file_path]

        report_df = get_ir_report_df(pair, coded_columns, ids=row_ids, id_column='id')
        all_code_comparison['Code'] = report_df['Code']
        all_code_comparison['Gold Standard Count'] = report_df['Coder 1']
        all_code_comparison[k] = report_df['Kappa']

    df = pd.DataFrame(all_code_comparison)

    # Calculate average row
    numeric_columns = df.select_dtypes(include=['number']).columns
    average_row = df[numeric_columns].mean().to_frame().T
    average_row['Code'] = 'Average'
    df = pd.concat([df, average_row], ignore_index=True)

    return df


def main():
    """Main analysis function."""
    print("=" * 80)
    print("Replicating Analysis: Scalable Qualitative Coding with LLMs")
    print("=" * 80)

    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Run gold standard vs GPT comparison
    print("\nCalculating intercoder reliability metrics...")
    comparison_df = gold_standard_vs_gpt_comparison()

    print("\nResults:")
    print(comparison_df.to_string(index=False))

    # Save results
    output_file = 'results/outputs/intercoder_reliability_results.csv'
    comparison_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")

    # Also generate individual condition reports
    print("\nGenerating individual condition reports...")

    conditions = {
        'per-code-with-justification_gpt4': 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4',
        'per-code-without-justification_gpt4': 'results/raw/output_original/per-code-without-justification_t=0_top_p=1_model=gpt-4',
        'full-codebook-with-justification_gpt4': 'results/raw/output_original/full-codebook_with_justification_t=0_top_p=1_model=gpt-4',
        'full-codebook-without-justification_gpt4': 'results/raw/output_original/full-codebook_without_justification_t=0_top_p=1_model=gpt-4',
        'per-code-with-justification_gpt35': 'results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-3.5',
        'per-code-without-justification_gpt35': 'results/raw/output_original/per-code-without-justification_t=0_top_p=1_model=gpt-3.5',
    }

    for condition_name, dir_path in conditions.items():
        file_path = f'{dir_path}/processed_responses.csv'
        if os.path.exists(file_path):
            pair = ['data/processed/gold_standard_coding.csv', file_path]
            report_df = get_ir_report_df(pair, coded_columns, ids=row_ids, id_column='id')

            # Save detailed report
            detail_file = f'results/outputs/{condition_name}_detailed_report.csv'
            report_df.to_csv(detail_file, index=False)
            print(f"  - {condition_name}: saved to {detail_file}")

    print("\nAnalysis complete!")
    return comparison_df


if __name__ == "__main__":
    results = main()
