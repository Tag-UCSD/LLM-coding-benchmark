# Data Collection Resume Instructions

**Last Updated:** December 4, 2025, 3:45 AM
**Current Status:** Gemini collection IN PROGRESS

---

## Quick Summary

### What We're Doing
Running qualitative coding analysis on 111 W.E.B. Du Bois passages using multiple LLMs. We're collecting data for:
- **per-code-with-justification** (9 codes × 111 passages = 999 API calls)
- **full-codebook-with-justification** (1 × 111 passages = 111 API calls)

**IMPORTANT:** We are NOT running without-justification conditions to save API credits.

### Total Data Needed
- **Gemini:** 999 + 111 = 1,110 API calls
- **Llama (via Groq):** 999 + 111 = 1,110 API calls
- **Total:** 2,220 API calls

---

## Current Status (as of Dec 4, 2025 3:45 AM)

### Gemini (Google) - RUNNING NOW
**API Key:** YOUR_GEMINI_API_KEY
**Model:** gemini-2.5-flash-lite
**Rate Limit:** 15 requests/minute (free tier)
**Delay Between Requests:** 4.5 seconds

#### Per-Code Progress (out of 111 passages each):
```
scholar                       :  82/111  (29 remaining) ✓ IN PROGRESS
activist                      :  67/111  (44 remaining)
monumental-memorialization    :  70/111  (41 remaining)
mention-of-scholarly-work     :  70/111  (41 remaining)
social-political-advocacy     :  74/111  (37 remaining)
coalition-building            :  70/111  (41 remaining)
out-of-the-mouth-of-academics :  73/111  (38 remaining)
out-of-the-mouth-of-activists :  72/111  (39 remaining)
collective-synecdoche         :  73/111  (38 remaining)
```
**Total Per-Code:** 651/999 (348 remaining, ~65% complete)

#### Full-Codebook Progress:
```
Full-codebook: 13/111 (98 remaining, ~12% complete)
```

**Estimated Time Remaining:**
- Remaining calls: 348 + 98 = 446 calls
- At 4.5 seconds per call: 446 × 4.5 = 2,007 seconds ≈ **33 minutes**

**Current Process:**
- Process ID (PID): 22638
- Log file: `docs/internal/logs/gemini_collection.log`
- Script: `src/collection/resume_gemini.py`
- Status: ACTIVELY COLLECTING (verified Dec 4 3:45 AM)

---

### Llama (via Groq) - NOT STARTED (NEED API KEY)
**API Key:** **NEEDED** - Get free key at https://console.groq.com
**Model:** llama-3.3-70b-versatile
**Rate Limit:** Much higher than Gemini (Groq is very fast)

#### Per-Code Status (out of 111 passages each):
```
scholar                       : 111/111  (COMPLETE ✓)
activist                      :  77/111  (34 remaining)
monumental-memorialization    :   1/111  (110 remaining)
mention-of-scholarly-work     :   3/111  (108 remaining)
social-political-advocacy     :   2/111  (109 remaining)
coalition-building            :   1/111  (110 remaining)
out-of-the-mouth-of-academics :   1/111  (110 remaining)
out-of-the-mouth-of-activists :   1/111  (110 remaining)
collective-synecdoche         :   2/111  (109 remaining)
```
**Total Per-Code:** 199/999 (800 remaining, ~20% complete)

#### Full-Codebook Status:
```
Full-codebook: NOT STARTED (0/111, 100% remaining)
```

**What to do:** Get Groq API key and run `src/collection/resume_llama.py` script.

---

## How to Resume Collection

### Option 1: Check Current Status First
```bash
cd "/path/to/repo"
python3 << 'EOF'
import glob

# Check Gemini
print("=== GEMINI STATUS ===")
for code in ['scholar', 'activist', 'monumental-memorialization', 'mention-of-scholarly-work',
             'social-political-advocacy', 'coalition-building', 'out-of-the-mouth-of-academics',
             'out-of-the-mouth-of-activists', 'collective-synecdoche']:
    path = f"results/raw/output_gemini/per-code-with-justification_t=0_top_p=1_model=gemini/{code}/message_*.txt"
    count = len(glob.glob(path))
    print(f"{code:30s}: {count:3d}/111")

gemini_full = len(glob.glob("results/raw/output_gemini/full-codebook_with-justification_t=0_top_p=1_model=gemini/message_*.txt"))
print(f"Full-codebook: {gemini_full}/111\n")

# Check Llama
print("=== LLAMA STATUS ===")
for code in ['scholar', 'activist', 'monumental-memorialization', 'mention-of-scholarly-work',
             'social-political-advocacy', 'coalition-building', 'out-of-the-mouth-of-academics',
             'out-of-the-mouth-of-activists', 'collective-synecdoche']:
    path = f"results/raw/output_llama/per-code-with-justification_t=0_model=llama-3.3-70b/{code}/message_*.txt"
    count = len(glob.glob(path))
    print(f"{code:30s}: {count:3d}/111")

import os
llama_full_dir = "results/raw/output_llama/full-codebook-with-justification_t=0_model=llama-3.3-70b/"
if os.path.exists(llama_full_dir):
    llama_full = len(glob.glob(f"{llama_full_dir}/message_*.txt"))
    print(f"Full-codebook: {llama_full}/111")
else:
    print("Full-codebook: NOT STARTED")
EOF
```

### Option 2: Resume Gemini Collection
```bash
cd "/path/to/repo"

# Check if already running
ps aux | grep -E "python.*gemini" | grep -v grep

# If not running, restart:
python3 src/collection/resume_gemini.py YOUR_GEMINI_API_KEY > docs/internal/logs/gemini_collection.log 2>&1 &

# Monitor progress:
tail -f docs/internal/logs/gemini_collection.log
```

### Option 3: Start Llama Collection (When You Have API Key)
```bash
cd "/path/to/repo"

# Get free API key from: https://console.groq.com
# Then run:
python3 src/collection/resume_llama.py YOUR_GROQ_API_KEY_HERE > docs/internal/logs/llama_collection.log 2>&1 &

# Monitor progress:
tail -f docs/internal/logs/llama_collection.log
```

### Option 4: Run Both in Parallel (RECOMMENDED)
```bash
cd "/path/to/repo"

# Terminal 1 - Gemini
python3 src/collection/resume_gemini.py YOUR_GEMINI_API_KEY > docs/internal/logs/gemini_collection.log 2>&1 &

# Terminal 2 - Llama (when you have key)
python3 src/collection/resume_llama.py YOUR_GROQ_API_KEY_HERE > docs/internal/logs/llama_collection.log 2>&1 &

# Check both logs:
tail -f docs/internal/logs/gemini_collection.log docs/internal/logs/llama_collection.log
```

---

## Important Notes

### Scripts Automatically Skip Existing Files
Both `src/collection/resume_gemini.py` and `src/collection/resume_llama.py` check for existing `message_*.txt` files and skip them. This means you can safely restart the scripts at any time without losing progress or making duplicate API calls.

### Rate Limiting
- **Gemini:** 4.5 seconds between requests (free tier: 15/minute)
- **Llama:** 0.5 seconds between requests (Groq is very fast and generous)

### Cost
- **Gemini:** FREE (using free tier)
- **Llama via Groq:** FREE (Groq provides free API access)
- **Total Cost:** $0

### Output Directories
- Gemini per-code: `results/raw/output_gemini/per-code-with-justification_t=0_top_p=1_model=gemini/`
- Gemini full: `results/raw/output_gemini/full-codebook_with-justification_t=0_top_p=1_model=gemini/`
- Llama per-code: `results/raw/output_llama/per-code-with-justification_t=0_model=llama-3.3-70b/`
- Llama full: `results/raw/output_llama/full-codebook-with-justification_t=0_model=llama-3.3-70b/`

### Unwanted Directories (DO NOT USE)
These contain partial data from without-justification conditions that we're NOT completing:
- `results/raw/output_gemini/per-code-without-justification_t=0_top_p=1_model=gemini/`
- `results/raw/output_gemini/full-codebook_without-justification_t=0_top_p=1_model=gemini/`

---

## What Happens Next (After Data Collection)

Once both Gemini and Llama finish collecting all 1,110 passages each:

1. **Process the results** (convert JSON to CSV):
   ```bash
   python3 src/processing/process_gemini_results.py
   python3 src/processing/process_llama_results.py
   ```

2. **Analyze intercoder reliability**:
   ```bash
   python3 src/analysis/analyze_gemini_results.py
   python3 src/analysis/analyze_llama_results.py
   ```

3. **Create visualizations**:
   ```bash
   Rscript src/visualization/create_gemini_visualizations.R
   Rscript src/visualization/create_threeway_visualizations.R
   ```

4. **Compare all three models** (GPT-4, Gemini, Llama):
   - See `docs/reports/THREE_MODEL_COMPARISON.md` for analysis plan
   - Final output: Cohen's Kappa scores comparing all models

---

## Troubleshooting

### "Rate limit exceeded" Error
The scripts now have proper rate limiting built in. If you see this error in old logs, it's from before the fix. Just restart with `src/collection/resume_gemini.py` or `src/collection/resume_llama.py`.

### Check if Process is Running
```bash
ps aux | grep -E "python.*(gemini|llama)" | grep -v grep
```

### Kill Stuck Process
```bash
# Find the PID
ps aux | grep -E "python.*(gemini|llama)" | grep -v grep

# Kill it (replace 12345 with actual PID)
kill 12345
```

### Check Progress Without Logs
Use Option 1 above (status check script) to see current file counts.

---

## Files Created for This Project

### Runner Scripts (NEW)
- `src/collection/resume_gemini.py` - Resumes Gemini collection (with-justification only)
- `src/collection/resume_llama.py` - Resumes Llama collection (with-justification only)

### Modified Scripts
- `groq_coding_workflow.py` - Added `run_full_codebook_llama()` function
- `gemini_coding_workflow.py` - Fixed rate limiting (0.5s → 4.5s)

### Original Scripts (Unchanged)
- `gemini_coding_workflow.py` - Gemini API calling
- `groq_coding_workflow.py` - Llama/Groq API calling
- `src/processing/process_gemini_results.py` - Process Gemini outputs
- `src/processing/process_llama_results.py` - Process Llama outputs
- `src/analysis/analyze_gemini_results.py` - Calculate metrics
- `src/analysis/analyze_llama_results.py` - Calculate metrics

---

## Contact/Questions

**For the next session:**
1. Check current status (Option 1)
2. Resume Gemini if not complete (Option 2)
3. Get Groq API key and start Llama (Option 3)
4. Run both in parallel for fastest completion (Option 4)

**Current Gemini API Key:** YOUR_GEMINI_API_KEY
**Groq API Key:** Get free at https://console.groq.com (no credit card needed)

---

**Status as of Dec 4, 2025 3:45 AM:**
- ✅ Gemini: ACTIVELY COLLECTING (~65% complete, ~33 min remaining)
- ⏳ Llama: WAITING FOR API KEY (~20% complete when started)
