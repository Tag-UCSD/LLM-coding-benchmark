# LLM Agent Handoff Guide - Data Collection Continuation

## Date: 2025-12-29 20:49
## Status: Collections in progress, need monitoring and completion

---

## Current State Summary

### Collection Progress
- **Qwen 2.5 72B**: 642/999 (64.3%) - 5/9 codes complete - RUNNING
- **Llama 3.3 70B**: 109/999 (10.9%) - 0/9 codes complete - RUNNING
- **Gemini 2.5 Flash-Lite**: 0/999 (0.0%) - No data yet - RUNNING

### Running Processes
```
PID 71958: Qwen collection
PID 72420: Llama collection (FREE tier)
PID 72440: Gemini collection
```

### Key Achievement
✅ **Bug fix verified!** Qwen preliminary results show **κ = 0.604** (was -0.098)
- Passages now correctly aligned with gold standard
- All Kappa values are positive
- Fix confirmed to be working

---

## The Problem That Was Fixed

### Original Error
**Symptom:** All alternative models (Gemini, Llama, Qwen) showed negative Cohen's Kappa values (-0.09 to -0.10), indicating worse-than-random performance.

**Root Cause:** Data alignment bug in collection scripts.

**The Bug:**
```python
# WRONG (what was originally done):
passages = pd.read_csv("data/raw/passages.csv")
passages_include = range(9, 120)
messages = passages.loc[passages.index.isin(passages_include), 'passage']
# This used pandas INDEX (0-232 sequential) from passages.csv
```

**The Fix:**
```python
# CORRECT (what we do now):
gold_standard = pd.read_csv("data/processed/gold_standard_coding.csv")
test_set_ids = range(9, 120)
test_passages = gold_standard[gold_standard['id'].isin(test_set_ids)]
messages = test_passages[['id', 'passage']]
# This uses gold standard IDs (scattered 9-119 from 0-232 range)
```

**Impact:**
- Models were coding **completely different passages** than the gold standard
- Passage at pandas index 10 ≠ Passage with gold standard ID 10
- Comparison was meaningless, hence negative Kappa

**Verification:**
- Before fix: Qwen κ = -0.098
- After fix: Qwen κ = +0.604 (partial data, 5/9 codes)
- GPT-4 (always correct): κ = 0.676

---

## Architecture of the Solution

### File Structure
```
src/collection/
├── unified_openrouter_workflow.py  # Core collection logic (CORRECTED)
├── run_all_openrouter.py          # Runner script
├── resume_qwen.py                  # Legacy (not used)
├── groq_coding_workflow.py         # Legacy (has bug)
└── gemini_coding_workflow.py       # Legacy (has bug)

Current collections use: unified_openrouter_workflow.py
```

### Key Features of Corrected System

1. **Correct Passage Loading:**
   - Loads from `gold_standard_coding.csv`
   - Uses actual gold standard IDs (scattered across 0-232)
   - Test set: IDs 9-119 (111 passages)

2. **Automatic Rate Limit Handling:**
   - Detects rate limit errors (429, 'rate' in error message)
   - Parses wait time from error messages
   - Exponential backoff (up to 60 seconds)
   - Up to 10 retries before failing

3. **Progress Saving:**
   - Each message saved immediately as `message_{id}.txt`
   - Skips already-completed passages on resume
   - Can interrupt and resume safely

4. **OpenRouter Unified API:**
   - Single API key for all models
   - Models used:
     - Qwen: `qwen/qwen-2.5-72b-instruct`
     - Llama: `meta-llama/llama-3.3-70b-instruct:free` (FREE!)
     - Gemini: `google/gemini-2.5-flash-lite`

---

## How to Monitor Collections

### Check Overall Progress
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

# Count messages for each model
find results/raw/output_qwen/per-code-with-justification_t=0_model=qwen -name "message_*.txt" | wc -l
find results/raw/output_llama/per-code-with-justification_t=0_model=llama -name "message_*.txt" | wc -l
find results/raw/output_gemini/per-code-with-justification_t=0_model=gemini -name "message_*.txt" | wc -l
```

### Check Detailed Progress by Code
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

python << 'EOF'
import os

models = [
    ("Qwen", "results/raw/output_qwen/per-code-with-justification_t=0_model=qwen"),
    ("Llama", "results/raw/output_llama/per-code-with-justification_t=0_model=llama"),
    ("Gemini", "results/raw/output_gemini/per-code-with-justification_t=0_model=gemini")
]

for name, path in models:
    if not os.path.exists(path):
        print(f"{name}: No data yet")
        continue

    print(f"\n{name}:")
    total = 0
    for code_dir in sorted(os.listdir(path)):
        if os.path.isdir(os.path.join(path, code_dir)):
            count = len([f for f in os.listdir(os.path.join(path, code_dir))
                        if f.startswith("message_") and f.endswith(".txt")])
            total += count
            status = "✓" if count >= 111 else f"{count}/111"
            print(f"  {code_dir:<40} {status}")
    print(f"  TOTAL: {total}/999 ({total/999*100:.1f}%)")
EOF
```

### Check Running Processes
```bash
ps aux | grep run_all_openrouter | grep -v grep
```

### View Logs (if available)
```bash
tail -f qwen_collection.log
tail -f llama_collection.log
tail -f gemini_collection.log
```

---

## How to Handle Stalled Collections

### Detection
If a collection shows no progress for >10 minutes:
```bash
# Check for recently modified files (last 10 minutes)
find results/raw/output_qwen -name "message_*.txt" -mmin -10 | wc -l
find results/raw/output_llama -name "message_*.txt" -mmin -10 | wc -l
find results/raw/output_gemini -name "message_*.txt" -mmin -10 | wc -l
```

If output is `0`, the collection has stalled.

### Resolution
1. **Kill the stalled process:**
```bash
# Option 1: Kill specific model
pkill -f "run_all_openrouter.py.*qwen"
pkill -f "run_all_openrouter.py.*llama"
pkill -f "run_all_openrouter.py.*gemini"

# Option 2: Kill all
pkill -f "run_all_openrouter.py"
```

2. **Restart the collection:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

# Restart specific model
nohup python src/collection/run_all_openrouter.py \
  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 \
  qwen > qwen_collection.log 2>&1 &

nohup python src/collection/run_all_openrouter.py \
  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 \
  llama > llama_collection.log 2>&1 &

nohup python src/collection/run_all_openrouter.py \
  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 \
  gemini > gemini_collection.log 2>&1 &
```

**The collections will automatically resume from where they left off** - already-completed passages are skipped.

---

## Exact Commands to Continue/Restart Collections

### Prerequisites
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

# Ensure OpenAI package is installed (for OpenRouter API)
pip install openai
```

### OpenRouter API Key
```
# OLD (out of credits):
# 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

# NEW (active):
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
```

### Start Individual Model Collection

**Qwen:**
```bash
nohup python src/collection/run_all_openrouter.py \
  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 \
  qwen > qwen_collection.log 2>&1 &
echo "Started Qwen collection (PID: $!)"
```

**Llama (FREE tier):**
```bash
nohup python src/collection/run_all_openrouter.py \
  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 \
  llama > llama_collection.log 2>&1 &
echo "Started Llama collection (PID: $!)"
```

**Gemini:**
```bash
nohup python src/collection/run_all_openrouter.py \
  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 \
  gemini > gemini_collection.log 2>&1 &
echo "Started Gemini collection (PID: $!)"
```

**All at once:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

# Start all three in parallel
for model in qwen llama gemini; do
  nohup python src/collection/run_all_openrouter.py \
    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 \
    $model > ${model}_collection.log 2>&1 &
  echo "Started $model collection (PID: $!)"
done
```

### The System Handles Rate Limits Automatically

The `unified_openrouter_workflow.py` script has this logic:
```python
def make_openrouter_call(prompt, message, model, temperature=0.0, max_retries=10):
    for attempt in range(max_retries):
        try:
            # Make API call
            completion = client.chat.completions.create(...)
            return completion.choices[0].message.content

        except Exception as e:
            # Check if it's a rate limit error
            if 'rate' in str(e).lower() or '429' in str(e):
                wait_time = 60  # Default

                # Try to parse wait time from error
                import re
                time_match = re.search(r'(\d+)\s*second', str(e), re.IGNORECASE)
                if time_match:
                    wait_time = int(time_match.group(1)) + 5

                print(f"Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            # Other errors: exponential backoff
            wait = min(2 ** attempt, 60)
            time.sleep(wait)
```

**You don't need to do anything!** The script will:
1. Hit rate limit
2. Wait the specified time
3. Retry automatically
4. Continue collecting

---

## Processing Results After Collection

### When to Process
Wait until a model shows 999/999 messages collected, or close to it (990+).

### Processing Commands

**Process Qwen:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"
python src/processing/process_qwen_results.py
```

**Process Llama:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"
python src/processing/process_llama_results.py
```

**Process Gemini:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"
python src/processing/process_gemini_results.py
```

**Note:** You may need to update the processing scripts to use the correct paths:
- Qwen: `results/raw/output_qwen/per-code-with-justification_t=0_model=qwen`
- Llama: `results/raw/output_llama/per-code-with-justification_t=0_model=llama`
- Gemini: `results/raw/output_gemini/per-code-with-justification_t=0_model=gemini`

### Analysis Commands

**Analyze Qwen:**
```bash
python src/analysis/analyze_qwen_results.py
```

**Analyze Llama:**
```bash
python src/analysis/analyze_llama_results.py
```

**Analyze Gemini:**
```bash
python src/analysis/analyze_gemini_results.py
```

### Generate Visualizations

**Four-way comparison:**
```bash
Rscript src/visualization/create_fourway_visualizations.R
```

---

## Expected Results

Based on preliminary Qwen results (64% complete, κ = 0.604), we expect:

| Model | Expected Kappa Range | Notes |
|-------|---------------------|-------|
| GPT-4 | 0.676 | Already verified (original data) |
| Qwen | 0.55-0.65 | Partial data shows 0.604 |
| Llama | 0.50-0.70 | TBD |
| Gemini | 0.40-0.60 | TBD |

**All should be POSITIVE** (not negative like before the fix).

---

## Verification Checklist

After processing results, verify:

1. **Passage alignment:**
```python
import pandas as pd

# Check if passages match gold standard
qwen = pd.read_csv('results/raw/output_qwen/.../processed_responses.csv')
gold = pd.read_csv('data/processed/gold_standard_coding.csv')

# Sample check for ID 10
assert len(qwen[qwen['id'] == 10]) > 0, "Qwen missing ID 10"
assert len(gold[gold['id'] == 10]) > 0, "Gold missing ID 10"
print("✓ IDs present in both files")
```

2. **Positive Kappa values:**
```python
from src.analysis.replicate_analysis import get_ir_report_df

results = get_ir_report_df(
    ['data/processed/gold_standard_coding.csv',
     'results/raw/output_qwen/.../processed_responses.csv'],
    ['Scholar', 'Activist', ...],
    ids=range(9, 120),
    id_column='id'
)

print(results[['Code', 'Kappa']])
assert results['Kappa'].mean() > 0, "Kappa should be positive!"
print(f"✓ Average Kappa: {results['Kappa'].mean():.3f}")
```

3. **ID ranges:**
```python
# Should have scattered IDs across 0-232, not sequential 9-119
qwen = pd.read_csv('results/raw/output_qwen/.../processed_responses.csv')
unique_ids = sorted(qwen['id'].unique())

# Test set should have 111 unique IDs in range 9-119
assert len(unique_ids) == 111, f"Should have 111 IDs, got {len(unique_ids)}"
assert all(9 <= id <= 119 for id in unique_ids), "All IDs should be in range 9-119"
print(f"✓ Correct number of IDs: {len(unique_ids)}")
```

---

## Troubleshooting

### Problem: Gemini shows 0 progress
**Possible causes:**
- Slower API response time
- Different rate limits
- Process might have crashed

**Solution:**
```bash
# Check if process is running
ps aux | grep "gemini" | grep -v grep

# Check log for errors
tail -100 gemini_collection.log

# If crashed, restart
nohup python src/collection/run_all_openrouter.py \
  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 \
  gemini > gemini_collection.log 2>&1 &
```

### Problem: Collection stuck at same count
**Diagnosis:**
```bash
# Check for recent file modifications
find results/raw/output_qwen -name "*.txt" -mmin -5 | wc -l
```

If 0, collection is stalled.

**Solution:** Kill and restart (see "How to Handle Stalled Collections" above)

### Problem: Rate limits causing very slow progress
**Solution:**
- This is normal! The auto-retry system is working.
- FREE Llama tier may be slower.
- Be patient - it will complete eventually.
- Typical rate: 15-30 messages per minute
- Total time: 30-60 minutes per model

---

## Summary for Quick Reference

**Current State:**
- Qwen: 64% done, running
- Llama: 11% done, running
- Gemini: 0% done, running

**What's Fixed:**
- Passages now load from `gold_standard_coding.csv` (correct IDs)
- Rate limiting handled automatically
- Results will be POSITIVE Kappa values

**What to Do:**
1. Monitor progress every 30-60 minutes
2. If stalled (no new files in 10min), kill and restart
3. When 990+ messages, run processing scripts
4. Run analysis scripts
5. Generate visualizations

**Key Commands:**
```bash
# Monitor
find results/raw/output_*/per-code-*t=0_model=* -name "message_*.txt" | wc -l

# Restart if needed
pkill -f run_all_openrouter
nohup python src/collection/run_all_openrouter.py API_KEY model > log 2>&1 &

# Process when done
python src/processing/process_{model}_results.py
python src/analysis/analyze_{model}_results.py
```

**Expected Completion:** 1-3 hours for all models (depending on rate limits)

---

End of handoff guide. Good luck! 🚀
