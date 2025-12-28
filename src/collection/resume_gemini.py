"""
Resume Gemini data collection - WITH JUSTIFICATION ONLY
Automatically skips already-coded passages
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from gemini_coding_workflow import (
    initialize_gemini,
    run_per_code_coding,
    run_full_codebook_coding
)

def resume_gemini_with_justification(api_key):
    """Resume Gemini coding for with-justification conditions only."""

    print("=" * 80)
    print("RESUMING GEMINI DATA COLLECTION")
    print("Conditions: WITH JUSTIFICATION ONLY")
    print("=" * 80)

    # Initialize Gemini
    initialize_gemini(api_key)

    # Model parameters (same as original)
    model = "gemini-2.5-flash-lite"
    temperature = 0
    top_p = 1

    paths_created = []

    # 1. Per-code with justification
    print("\n" + "=" * 80)
    print("1/2: PER-CODE WITH JUSTIFICATION")
    print("=" * 80)
    path = run_per_code_coding(
        model=model,
        temperature=temperature,
        top_p=top_p,
        with_justification=True
    )
    paths_created.append(path)

    # 2. Full codebook with justification
    print("\n" + "=" * 80)
    print("2/2: FULL-CODEBOOK WITH JUSTIFICATION")
    print("=" * 80)
    path = run_full_codebook_coding(
        model=model,
        temperature=temperature,
        top_p=top_p,
        with_justification=True
    )
    paths_created.append(path)

    print("\n" + "=" * 80)
    print("GEMINI COLLECTION COMPLETE!")
    print("=" * 80)
    print(f"\nCompleted conditions:")
    for path in paths_created:
        print(f"  ✓ {path}")

    return paths_created


if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        resume_gemini_with_justification(api_key)
    else:
        print("\nUsage:")
        print("  python src/collection/resume_gemini.py YOUR_GEMINI_API_KEY")
        print("\nOr in Python:")
        print("  from resume_gemini import resume_gemini_with_justification")
        print("  resume_gemini_with_justification('YOUR_API_KEY')")
