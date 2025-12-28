#!/usr/bin/env python3
"""
Quick status checker for data collection progress
Run this anytime to see current status
"""

import glob
import os
import time
from datetime import datetime

codes = ['scholar', 'activist', 'monumental-memorialization', 'mention-of-scholarly-work',
         'social-political-advocacy', 'coalition-building', 'out-of-the-mouth-of-academics',
         'out-of-the-mouth-of-activists', 'collective-synecdoche']

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

total_per_code = 111
total_codes = 9

print("=" * 80)
print(f"DATA COLLECTION STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Gemini status
print("\n=== GEMINI (Google) ===")
print("Model: gemini-2.5-flash-lite")
print("\nPer-Code Progress (with justification):")

gemini_per_code_total = 0
for code in codes:
    path = os.path.join(
        BASE_DIR,
        "results/raw/output_gemini/per-code-with-justification_t=0_top_p=1_model=gemini",
        code,
        "message_*.txt",
    )
    files = glob.glob(path)
    count = len(files)
    gemini_per_code_total += count
    remaining = total_per_code - count
    pct = (count / total_per_code) * 100

    # Check if actively being updated
    status = ""
    if files:
        most_recent = max(files, key=os.path.getmtime)
        mod_time = os.path.getmtime(most_recent)
        seconds_ago = time.time() - mod_time
        if seconds_ago < 60:
            status = " ✓ ACTIVE"

    print(f"  {code:30s}: {count:3d}/{total_per_code} ({pct:5.1f}%, {remaining:3d} left){status}")

gemini_per_code_pct = (gemini_per_code_total / (total_codes * total_per_code)) * 100
print(f"\n  TOTAL PER-CODE: {gemini_per_code_total}/{total_codes * total_per_code} ({gemini_per_code_pct:.1f}%)")

print("\nFull-Codebook Progress (with justification):")
gemini_full = len(
    glob.glob(
        os.path.join(
            BASE_DIR,
            "results/raw/output_gemini/full-codebook_with-justification_t=0_top_p=1_model=gemini",
            "message_*.txt",
        )
    )
)
gemini_full_pct = (gemini_full / total_per_code) * 100
print(f"  {gemini_full}/{total_per_code} ({gemini_full_pct:.1f}%)")

gemini_total = gemini_per_code_total + gemini_full
gemini_total_needed = (total_codes * total_per_code) + total_per_code
gemini_overall_pct = (gemini_total / gemini_total_needed) * 100
print(f"\n  GEMINI OVERALL: {gemini_total}/{gemini_total_needed} ({gemini_overall_pct:.1f}%)")

# Llama status
print("\n=== LLAMA (via Groq) ===")
print("Model: llama-3.3-70b-versatile")
print("\nPer-Code Progress (with justification):")

llama_per_code_total = 0
for code in codes:
    path = os.path.join(
        BASE_DIR,
        "results/raw/output_llama/per-code-with-justification_t=0_model=llama-3.3-70b",
        code,
        "message_*.txt",
    )
    files = glob.glob(path)
    count = len(files)
    llama_per_code_total += count
    remaining = total_per_code - count
    pct = (count / total_per_code) * 100

    # Check if actively being updated
    status = ""
    if files:
        most_recent = max(files, key=os.path.getmtime)
        mod_time = os.path.getmtime(most_recent)
        seconds_ago = time.time() - mod_time
        if seconds_ago < 60:
            status = " ✓ ACTIVE"

    print(f"  {code:30s}: {count:3d}/{total_per_code} ({pct:5.1f}%, {remaining:3d} left){status}")

llama_per_code_pct = (llama_per_code_total / (total_codes * total_per_code)) * 100
print(f"\n  TOTAL PER-CODE: {llama_per_code_total}/{total_codes * total_per_code} ({llama_per_code_pct:.1f}%)")

print("\nFull-Codebook Progress (with justification):")
llama_full_dir = os.path.join(
    BASE_DIR,
    "results/raw/output_llama/full-codebook-with-justification_t=0_model=llama-3.3-70b",
)
if os.path.exists(llama_full_dir):
    llama_full = len(glob.glob(f"{llama_full_dir}/message_*.txt"))
    llama_full_pct = (llama_full / total_per_code) * 100
    print(f"  {llama_full}/{total_per_code} ({llama_full_pct:.1f}%)")
else:
    llama_full = 0
    print(f"  NOT STARTED")

llama_total = llama_per_code_total + llama_full
llama_total_needed = (total_codes * total_per_code) + total_per_code
llama_overall_pct = (llama_total / llama_total_needed) * 100
print(f"\n  LLAMA OVERALL: {llama_total}/{llama_total_needed} ({llama_overall_pct:.1f}%)")

# Overall status
print("\n" + "=" * 80)
print("COMBINED STATUS")
print("=" * 80)
total_collected = gemini_total + llama_total
total_needed = gemini_total_needed + llama_total_needed
overall_pct = (total_collected / total_needed) * 100
print(f"Total API calls completed: {total_collected}/{total_needed} ({overall_pct:.1f}%)")
print(f"Remaining: {total_needed - total_collected} API calls")

# Estimate time remaining for Gemini
gemini_remaining = gemini_total_needed - gemini_total
if gemini_remaining > 0:
    gemini_time_estimate = gemini_remaining * 4.5  # 4.5 seconds per call
    gemini_minutes = gemini_time_estimate / 60
    print(f"\nGemini estimated time remaining: {gemini_minutes:.0f} minutes ({gemini_remaining} calls @ 4.5s each)")

# Check if processes are running
print("\n" + "=" * 80)
print("ACTIVE PROCESSES")
print("=" * 80)
import subprocess
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    gemini_procs = [line for line in result.stdout.split('\n') if 'gemini' in line.lower() and 'python' in line and 'grep' not in line]
    llama_procs = [line for line in result.stdout.split('\n') if 'llama' in line.lower() and 'python' in line and 'grep' not in line]

    if gemini_procs:
        print("✓ Gemini collection process RUNNING")
    else:
        print("✗ Gemini collection process NOT RUNNING")
        if gemini_remaining > 0:
            print("  → Run: python3 src/collection/resume_gemini.py YOUR_GEMINI_API_KEY")

    if llama_procs:
        print("✓ Llama collection process RUNNING")
    else:
        print("✗ Llama collection process NOT RUNNING")
        if llama_total < llama_total_needed:
            print("  → Run: python3 resume_llama.py YOUR_GROQ_API_KEY")
except:
    print("Unable to check running processes")

print("=" * 80)
