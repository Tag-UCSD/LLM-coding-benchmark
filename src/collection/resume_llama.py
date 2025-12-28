"""
Resume Llama data collection - WITH JUSTIFICATION ONLY
Automatically skips already-coded passages
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from groq_coding_workflow import (
    initialize_groq,
    run_per_code_llama,
    run_full_codebook_llama
)

def resume_llama_with_justification(api_key):
    """Resume Llama coding for with-justification conditions only."""

    print("=" * 80)
    print("RESUMING LLAMA DATA COLLECTION")
    print("Conditions: WITH JUSTIFICATION ONLY")
    print("=" * 80)

    paths_created = []

    # 1. Per-code with justification
    print("\n" + "=" * 80)
    print("1/2: PER-CODE WITH JUSTIFICATION")
    print("=" * 80)
    path = run_per_code_llama(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        with_justification=True
    )
    paths_created.append(path)

    # 2. Full codebook with justification
    print("\n" + "=" * 80)
    print("2/2: FULL-CODEBOOK WITH JUSTIFICATION")
    print("=" * 80)
    path = run_full_codebook_llama(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        with_justification=True
    )
    paths_created.append(path)

    print("\n" + "=" * 80)
    print("LLAMA COLLECTION COMPLETE!")
    print("=" * 80)
    print(f"\nCompleted conditions:")
    for path in paths_created:
        print(f"  ✓ {path}")

    return paths_created


if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        resume_llama_with_justification(api_key)
    else:
        print("\nUsage:")
        print("  python src/collection/resume_llama.py YOUR_GROQ_API_KEY")
        print("\nOr in Python:")
        print("  from resume_llama import resume_llama_with_justification")
        print("  resume_llama_with_justification('YOUR_API_KEY')")
        print("\nGet a free Groq API key at: https://console.groq.com")
