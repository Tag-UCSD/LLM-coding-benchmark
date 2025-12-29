"""
Resume Qwen data collection - PER-CODE WITH JUSTIFICATION
Automatically skips already-coded passages
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from openrouter_coding_workflow import (
    initialize_openrouter,
    run_per_code_qwen
)

def resume_qwen_with_justification(api_key):
    """Resume Qwen coding for with-justification condition (per-code only)."""

    print("=" * 80)
    print("RESUMING QWEN DATA COLLECTION")
    print("Conditions: PER-CODE WITH JUSTIFICATION ONLY")
    print("=" * 80)

    paths_created = []

    # Per-code with justification (best performing approach)
    print("\n" + "=" * 80)
    print("PER-CODE WITH JUSTIFICATION")
    print("=" * 80)
    path = run_per_code_qwen(
        api_key=api_key,
        model="qwen/qwen-2.5-72b-instruct",
        with_justification=True
    )
    paths_created.append(path)

    print("\n" + "=" * 80)
    print("QWEN COLLECTION COMPLETE!")
    print("=" * 80)
    print(f"\nCompleted conditions:")
    for path in paths_created:
        print(f"  ✓ {path}")

    return paths_created


if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        resume_qwen_with_justification(api_key)
    else:
        print("\nUsage:")
        print("  python src/collection/resume_qwen.py YOUR_OPENROUTER_API_KEY")
        print("\nOr in Python:")
        print("  from resume_qwen import resume_qwen_with_justification")
        print("  resume_qwen_with_justification('YOUR_API_KEY')")
        print("\nGet a free OpenRouter API key at: https://openrouter.ai")
