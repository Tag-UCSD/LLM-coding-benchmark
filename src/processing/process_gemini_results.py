"""
Process Gemini API responses into tabular format
"""

import pandas as pd
import os
import re
import glob


def extract_doc_id(filename):
    """Extracts the integer between '_' and '.txt' in the filename."""
    match = re.search(r'_(\d+)\.txt', filename)
    return int(match.group(1)) if match else None


def process_file_content(file_content):
    """Finds the last instance of 'codes applied' and stores all text after it."""
    file_content_lower = file_content.lower()
    codes_start = file_content_lower.rfind('codes applied')
    return file_content_lower[codes_start + len('codes applied'):].strip() if codes_start != -1 else ""


def match_pattern(pattern, string):
    """Check if a code pattern is present in the response."""
    # Match "scholar" only as a standalone word
    if pattern == "scholar":
        return bool(re.search(r'\bscholar\b', string))

    # Exact match for "scholarly work"
    if pattern == "scholarly work" and pattern == string:
        return True

    # Substring match for other patterns
    return bool(re.search(pattern, string))


def extract_codes_from_gemini_responses_full_codebook(path, codes):
    """Extract codes from full codebook responses."""
    file_pattern = os.path.join(path, 'message_*.txt')
    data = []

    # Read each .txt file and process the content
    codes_lower = [code.lower() for code in codes]
    for file_path in glob.glob(file_pattern):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            doc_id = extract_doc_id(file_path)
            codes_applied_string = process_file_content(content)

            # Check for the presence of each code
            code_presence = [1 if match_pattern(code, codes_applied_string) else 0 for code in codes_lower]

            # Append the result to the data list
            data.append([doc_id] + code_presence + [content])

    # Create a DataFrame
    columns = ['id'] + codes + ['file_contents']
    df = pd.DataFrame(data, columns=columns)

    return df


def extract_codes_from_gemini_responses_per_code(path, codes):
    """Extract codes from per-code responses."""
    data = {}

    # Read each .txt file and process the content
    for code in codes:
        code_path_name = code.lower().replace(' ', '-').replace('/', '-')
        file_pattern = os.path.join(path, code_path_name, 'message_*.txt')

        code_lower = code.lower()
        code_vector = []
        ids = []
        passages = []

        for file_path in glob.glob(file_pattern):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                doc_id = extract_doc_id(file_path)
                codes_applied_string = process_file_content(content)

                # Check for the presence of each code
                code_presence = 0
                if match_pattern(code_lower, codes_applied_string):
                    code_presence = 1

                code_vector.append(code_presence)
                ids.append(int(doc_id))

                # Extract passage
                match = re.search(r'User:\s*(.*?)[\s\n]*Assistant:', content, re.DOTALL)
                passage = match.group(1) if match else ""
                passages.append(passage)

        data[code] = {'code': code_vector, 'id': ids, 'passage': passages}

    # Merge all DataFrames
    dfs = []
    for code_name, values in data.items():
        df = pd.DataFrame(values)
        df = df.rename(columns={"code": code_name})
        dfs.append(df)

    # Merge all DataFrames on 'ids' and 'passage'
    df_final = pd.DataFrame()
    for df in dfs:
        if df_final.empty:
            df_final = df
        else:
            df_final = pd.merge(df_final, df.drop('passage', axis=1), on=["id"], how="outer")

    columns = list(df_final.columns)
    columns.remove('id')
    columns.remove('passage')
    rearranged_columns = ['id'] + columns + ['passage']
    df_final = df_final[rearranged_columns]

    return df_final


def process_all_gemini_outputs():
    """Process all Gemini output directories."""

    code_names = ['Scholar', 'Activist',
                  'Monumental Memorialization', 'Mention of Scholarly Work',
                  'Social/Political Advocacy', 'Coalition Building',
                  'Out of the Mouth of Academics', 'Out of the Mouth of Activists',
                  'Collective Synecdoche']

    print("=" * 80)
    print("PROCESSING GEMINI OUTPUTS")
    print("=" * 80)

    # Find all output directories
    base_dir = 'results/raw/output_gemini'
    if not os.path.exists(base_dir):
        print(f"No Gemini outputs found at {base_dir}")
        return

    # Process each condition
    for condition_dir in os.listdir(base_dir):
        condition_path = os.path.join(base_dir, condition_dir)

        if not os.path.isdir(condition_path):
            continue

        print(f"\nProcessing: {condition_dir}")

        try:
            # Determine if this is per-code or full codebook
            if 'per-code' in condition_dir:
                df = extract_codes_from_gemini_responses_per_code(condition_path, code_names)
            else:  # full codebook
                df = extract_codes_from_gemini_responses_full_codebook(condition_path, code_names)

            # Save processed responses
            output_file = os.path.join(condition_path, 'processed_responses.csv')
            df.to_csv(output_file, index=False)
            print(f"  ✓ Saved: {output_file}")
            print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print("\n✓ Processing complete!")


if __name__ == "__main__":
    process_all_gemini_outputs()
