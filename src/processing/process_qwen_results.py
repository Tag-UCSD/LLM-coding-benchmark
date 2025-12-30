"""
Process Qwen (via OpenRouter) coding results into CSV format
"""

import pandas as pd
import re
import os
import glob

# Code definitions
codes_full = [
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


def extract_codes_from_qwen_responses_per_code(base_path, passages_include=range(9, 120)):
    """
    Extract codes from Qwen per-code responses.

    Args:
        base_path: Path to per-code responses (e.g., 'results/raw/output_qwen/per-code-with-justification_t=0_model=qwen-2.5-72b')
        passages_include: Range of passage IDs to include

    Returns:
        DataFrame with binary codes for each passage
    """

    def code_to_path(code):
        """Convert code name to directory path."""
        code = code.lower()
        code = re.sub(r'[^a-zA-Z0-9]+', '-', code)
        return code

    def extract_code_from_response(response_text, code_title):
        """Extract whether code was applied from a single response."""
        # Look for "Codes Applied:" section
        if '**Codes Applied:**' in response_text:
            codes_section = response_text.split('**Codes Applied:**')[1].strip()
            # Check if the code title appears in the section or if it says "None"
            if code_title in codes_section:
                return 1
            elif 'None' in codes_section or codes_section.strip() == '-':
                return 0
        return 0  # Default to not applied if unclear

    # Initialize results dataframe
    results = pd.DataFrame({
        'id': list(passages_include),
    })

    for code in codes_full:
        code_path = code_to_path(code)
        code_dir = f"{base_path}/{code_path}"

        if not os.path.exists(code_dir):
            print(f"Warning: Directory not found: {code_dir}")
            results[code] = 0
            continue

        # Extract codes for each passage
        code_values = []
        for passage_id in passages_include:
            response_file = f"{code_dir}/message_{passage_id}.txt"

            if os.path.exists(response_file):
                with open(response_file, 'r') as f:
                    content = f.read()
                    # Extract assistant response
                    if 'Assistant:' in content:
                        response = content.split('Assistant:')[1].strip()
                        code_applied = extract_code_from_response(response, code)
                        code_values.append(code_applied)
                    else:
                        code_values.append(0)
            else:
                print(f"Warning: Missing response for passage {passage_id}, code {code}")
                code_values.append(0)

        results[code] = code_values

    return results


def process_qwen_per_code_condition(condition_path):
    """Process a single Qwen per-code condition and save to CSV."""

    print(f"\nProcessing: {condition_path}")

    if not os.path.exists(condition_path):
        print(f"  ✗ Path does not exist: {condition_path}")
        return None

    # Extract codes
    df = extract_codes_from_qwen_responses_per_code(condition_path)

    # Save to CSV
    output_file = f"{condition_path}/processed_responses.csv"
    df.to_csv(output_file, index=False)

    print(f"  ✓ Processed {len(df)} passages with {len(codes_full)} codes")
    print(f"  ✓ Saved to: {output_file}")

    return df


def process_all_qwen_results():
    """Process all Qwen coding results."""

    print("=" * 80)
    print("PROCESSING QWEN RESULTS")
    print("=" * 80)

    conditions = [
        'results/raw/output_qwen/per-code-with-justification_t=0_model=qwen',
    ]

    results = {}
    for condition in conditions:
        df = process_qwen_per_code_condition(condition)
        if df is not None:
            results[condition] = df

    print("\n" + "=" * 80)
    print(f"✓ Processed {len(results)} conditions")
    print("=" * 80)

    return results


if __name__ == "__main__":
    process_all_qwen_results()
