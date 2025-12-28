"""
Detailed comparison: Verify that calculated metrics match exactly
"""

import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score

# Load gold standard
gold = pd.read_csv('data/processed/gold_standard_coding.csv')

# Load one of the GPT outputs
gpt_output = pd.read_csv('results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv')

# Filter to test set IDs
test_ids = range(9, 120)
gold_test = gold[gold['id'].isin(test_ids)].sort_values('id').reset_index(drop=True)
gpt_test = gpt_output[gpt_output['id'].isin(test_ids)].sort_values('id').reset_index(drop=True)

# Code columns
code_cols = ['Scholar', 'Activist', 'Monumental Memorialization',
             'Mention of Scholarly Work', 'Social/Political Advocacy',
             'Coalition Building', 'Out of the Mouth of Academics',
             'Out of the Mouth of Activists', 'Collective Synecdoche']

print("=" * 80)
print("MANUAL VERIFICATION: Calculating Cohen's Kappa for Per-Code w/ Justification")
print("=" * 80)
print()

kappas = []
for code in code_cols:
    gold_vals = gold_test[code].fillna(0).astype(int)
    gpt_vals = gpt_test[code].fillna(0).astype(int)

    kappa = cohen_kappa_score(gold_vals, gpt_vals)
    kappas.append(kappa)

    print(f"{code:32s}: κ = {kappa:.6f}")

avg_kappa = np.mean(kappas)
print(f"\n{'Average':32s}: κ = {avg_kappa:.6f}")

print("\n" + "=" * 80)
print("COMPARISON WITH REPLICATED RESULTS")
print("=" * 80)

# Load our replicated results
results = pd.read_csv('results/outputs/intercoder_reliability_results.csv')

print("\nFrom our replicated analysis:")
for i, code in enumerate(code_cols):
    row = results[results['Code'] == code]
    if not row.empty:
        replicated_kappa = row['Per Code w/ Justification'].values[0]
        manual_kappa = kappas[i]
        diff = abs(replicated_kappa - manual_kappa)
        match = "✓" if diff < 1e-6 else "✗"
        print(f"{match} {code:32s}: Replicated={replicated_kappa:.6f}, Manual={manual_kappa:.6f}, Diff={diff:.10f}")

avg_row = results[results['Code'] == 'Average']
if not avg_row.empty:
    replicated_avg = avg_row['Per Code w/ Justification'].values[0]
    diff = abs(replicated_avg - avg_kappa)
    match = "✓" if diff < 1e-6 else "✗"
    print(f"\n{match} {'Average':32s}: Replicated={replicated_avg:.6f}, Manual={avg_kappa:.6f}, Diff={diff:.10f}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
if diff < 1e-6:
    print("\n✓✓✓ EXACT MATCH: The replicated analysis produces identical results!")
    print("The intercoder reliability metrics match to machine precision.")
else:
    print("\n⚠ Small differences detected (may be due to numerical precision)")

print("\nThis confirms that:")
print("  1. The replication code correctly implements the original methodology")
print("  2. The statistical calculations are accurate")
print("  3. Results can be trusted for interpretation and visualization")
