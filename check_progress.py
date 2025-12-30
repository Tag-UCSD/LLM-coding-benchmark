#!/usr/bin/env python3
"""
Quick progress checker for LLM data collection.
Run this script to see current status of all collections.

Usage:
    python check_progress.py
"""

import os
import subprocess
from datetime import datetime, timedelta

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def count_messages(base_path):
    """Count total messages and breakdown by code."""
    if not os.path.exists(base_path):
        return 0, {}

    total = 0
    breakdown = {}

    for code_dir in sorted(os.listdir(base_path)):
        code_path = os.path.join(base_path, code_dir)
        if os.path.isdir(code_path):
            count = len([f for f in os.listdir(code_path)
                        if f.startswith("message_") and f.endswith(".txt")])
            total += count
            breakdown[code_dir] = count

    return total, breakdown

def check_recent_activity(base_path, minutes=10):
    """Check if any files were modified in the last N minutes."""
    if not os.path.exists(base_path):
        return 0

    try:
        result = subprocess.run(
            ['find', base_path, '-name', 'message_*.txt', '-mmin', f'-{minutes}'],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 0

def check_running_processes():
    """Check if collection processes are running."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )

        processes = []
        for line in result.stdout.split('\n'):
            if 'run_all_openrouter.py' in line and 'grep' not in line:
                # Extract model name from command line
                if 'qwen' in line:
                    processes.append('qwen')
                elif 'llama' in line:
                    processes.append('llama')
                elif 'gemini' in line:
                    processes.append('gemini')

        return processes
    except:
        return []

def format_progress_bar(current, total, width=30):
    """Create a text progress bar."""
    if total == 0:
        percent = 0
    else:
        percent = (current / total) * 100

    filled = int(width * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (width - filled)

    return f"{bar} {current}/{total} ({percent:.1f}%)"

def print_model_status(model_name, base_path, color, total_expected=999):
    """Print status for a single model."""
    total, breakdown = count_messages(base_path)
    recent = check_recent_activity(base_path, minutes=10)

    print(f"\n{BOLD}{color}{model_name}{RESET}")
    print(f"  {format_progress_bar(total, total_expected)}")

    if recent > 0:
        print(f"  {GREEN}✓ ACTIVE{RESET} - {recent} files modified in last 10 minutes")
    else:
        print(f"  {RED}⚠ STALLED{RESET} - No activity in last 10 minutes")

    if breakdown:
        print(f"\n  {BOLD}Breakdown by code:{RESET}")
        for code, count in breakdown.items():
            status = f"{GREEN}✓{RESET}" if count >= 111 else f"{YELLOW}⚠{RESET}"
            print(f"    {status} {code:<40} {count:>3}/111")
    else:
        print(f"  {RED}No data collected yet{RESET}")

def main():
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}LLM Deductive Coding Benchmark - Collection Progress{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"{BLUE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

    # Check running processes
    running = check_running_processes()
    if running:
        print(f"\n{GREEN}✓ Running processes:{RESET} {', '.join(running)}")
    else:
        print(f"\n{RED}⚠ No collection processes running{RESET}")

    # Qwen status
    print_model_status(
        "Qwen 2.5 72B",
        "results/raw/output_qwen/per-code-with-justification_t=0_model=qwen",
        BLUE
    )

    # Llama status
    print_model_status(
        "Llama 3.3 70B (FREE tier)",
        "results/raw/output_llama/per-code-with-justification_t=0_model=llama",
        YELLOW
    )

    # Gemini status
    print_model_status(
        "Gemini 2.5 Flash-Lite",
        "results/raw/output_gemini/per-code-with-justification_t=0_model=gemini",
        GREEN
    )

    # Summary
    qwen_total, _ = count_messages("results/raw/output_qwen/per-code-with-justification_t=0_model=qwen")
    llama_total, _ = count_messages("results/raw/output_llama/per-code-with-justification_t=0_model=llama")
    gemini_total, _ = count_messages("results/raw/output_gemini/per-code-with-justification_t=0_model=gemini")

    grand_total = qwen_total + llama_total + gemini_total
    grand_expected = 999 * 3  # 3 models

    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Overall Progress:{RESET}")
    print(f"  {format_progress_bar(grand_total, grand_expected, width=50)}")
    print(f"\n  Qwen:   {qwen_total:>4}/999  ({qwen_total/999*100:>5.1f}%)")
    print(f"  Llama:  {llama_total:>4}/999  ({llama_total/999*100:>5.1f}%)")
    print(f"  Gemini: {gemini_total:>4}/999  ({gemini_total/999*100:>5.1f}%)")
    print(f"{BOLD}{'='*80}{RESET}\n")

if __name__ == "__main__":
    main()
