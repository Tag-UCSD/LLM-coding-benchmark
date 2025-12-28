#!/usr/bin/env python3
"""
Monitor Gemini coding progress in real-time
"""

import os
import time
import glob
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def count_files(pattern):
    """Count files matching pattern."""
    files = glob.glob(pattern)
    return len(files)

def get_progress():
    """Get current progress for all conditions."""
    base = os.path.join(BASE_DIR, "results", "raw", "output_gemini")

    conditions = {
        "Per-code WITH just": ("per-code-with-justification_t=0_top_p=1_model=gemini", 999),
        "Per-code W/OUT just": ("per-code-without-justification_t=0_top_p=1_model=gemini", 999),
        "Full WITH just": ("full-codebook_with-justification_t=0_top_p=1_model=gemini", 111),
        "Full W/OUT just": ("full-codebook_without-justification_t=0_top_p=1_model=gemini", 111),
    }

    results = {}
    total_done = 0
    total_expected = 0

    for name, (dir_name, expected) in conditions.items():
        path = os.path.join(base, dir_name)
        if os.path.exists(path):
            count = count_files(os.path.join(path, "**/message_*.txt"))
            results[name] = (count, expected)
            total_done += count
            total_expected += expected
        else:
            results[name] = (0, expected)
            total_expected += expected

    return results, total_done, total_expected

def print_progress():
    """Print formatted progress report."""
    results, total_done, total_expected = get_progress()

    print("\n" + "=" * 80)
    print(f"GEMINI CODING PROGRESS - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 80)

    for name, (done, expected) in results.items():
        pct = (done * 100 / expected) if expected > 0 else 0
        bar_length = 40
        filled = int(bar_length * done / expected) if expected > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"{name:20s} [{bar}] {done:4d}/{expected:4d} ({pct:5.1f}%)")

    print("-" * 80)
    total_pct = (total_done * 100 / total_expected) if total_expected > 0 else 0
    filled = int(40 * total_done / total_expected) if total_expected > 0 else 0
    bar = "█" * filled + "░" * (40 - filled)
    print(f"{'TOTAL':20s} [{bar}] {total_done:4d}/{total_expected:4d} ({total_pct:5.1f}%)")

    # Estimate time remaining
    if total_done > 0:
        # Assume ~2 seconds per call
        remaining_calls = total_expected - total_done
        est_seconds = remaining_calls * 2
        est_minutes = est_seconds / 60
        print(f"\nEstimated time remaining: {est_minutes:.1f} minutes")

    print("=" * 80)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        # Continuous monitoring
        try:
            while True:
                print_progress()
                time.sleep(60)  # Update every minute
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    else:
        # Single check
        print_progress()
