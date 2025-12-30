# Data Collection Status - Corrected Passages

## Date: 2025-12-30 (Final Update)

## ✅ **QWEN & GEMINI COMPLETE - ANALYZED & VISUALIZED**

## ✅ **BUG FIX VERIFIED - POSITIVE KAPPAS!**

### Final Results (All Codes Complete)

| Metric | Before Fix | After Fix (Qwen) | After Fix (Gemini) | Change |
|--------|-----------|------------------|-------------------|--------|
| **Average Kappa** | -0.098 | **+0.477** | **+0.487** | +0.575 avg ✓ |
| **% Agreement** | N/A | **87.5%** | **79.4%** | ✓ |
| Interpretation | Worse than random | Moderate agreement | Moderate agreement | **FIX WORKED!** |

**Qwen 2.5 72B - All 9 Codes:**
- Scholar: **κ = 0.404** (81.1% agreement)
- Activist: **κ = 0.549** (88.3% agreement)
- Monumental Memorialization: **κ = 0.955** (99.1% agreement) ⭐
- Mention of Scholarly Work: **κ = 0.539** (86.5% agreement)
- Social/Political Advocacy: **κ = 0.575** (79.3% agreement)
- Coalition Building: **κ = 0.000** (91.9% agreement)
- Out of the Mouth of Academics: **κ = 0.437** (82.0% agreement)
- Out of the Mouth of Activists: **κ = 0.085** (88.3% agreement)
- Collective Synecdoche: **κ = 0.749** (91.0% agreement)

**Gemini 2.5 Flash-Lite - All 9 Codes:**
- Scholar: **κ = 0.521** (78.4% agreement)
- Activist: **κ = 0.591** (82.9% agreement)
- Monumental Memorialization: **κ = 0.958** (99.1% agreement) ⭐
- Mention of Scholarly Work: **κ = 0.605** (83.8% agreement)
- Social/Political Advocacy: **κ = 0.592** (79.3% agreement)
- Coalition Building: **κ = 0.199** (78.4% agreement)
- Out of the Mouth of Academics: **κ = 0.438** (73.9% agreement)
- Out of the Mouth of Activists: **κ = 0.210** (80.2% agreement)
- Collective Synecdoche: **κ = 0.272** (58.6% agreement)

**Key Findings:** Both models show moderate agreement with gold standard. Very similar performance (κ ≈ 0.48), with different strengths across codes.

---

## Current Collection Status

### ✅ Qwen 2.5 72B - COMPLETE & ANALYZED
- **Status:** ✅ COMPLETE - 100% collected, processed, and analyzed
- **Progress:** 999/999 messages (100%)
- **Codes:** All 9 codes complete (111/111 each)
  - ✓ Scholar (111/111)
  - ✓ Activist (111/111)
  - ✓ Monumental Memorialization (111/111)
  - ✓ Mention of Scholarly Work (111/111)
  - ✓ Social/Political Advocacy (111/111)
  - ✓ Coalition Building (111/111)
  - ✓ Out of the Mouth of Academics (111/111)
  - ✓ Out of the Mouth of Activists (111/111)
  - ✓ Collective Synecdoche (111/111)
- **Analysis:** ✓ Complete
- **Visualizations:** ✓ Complete
- **Average Kappa:** **0.477** (87.5% agreement)

### ✅ Gemini 2.5 Flash-Lite - COMPLETE & ANALYZED
- **Status:** ✅ COMPLETE - 100% collected, processed, and analyzed
- **Model:** `google/gemini-2.5-flash-lite`
- **API:** OpenRouter
- **Progress:** 999/999 messages (100%)
- **Codes:** All 9 codes complete (111/111 each)
  - ✓ Scholar (111/111)
  - ✓ Activist (111/111)
  - ✓ Monumental Memorialization (111/111)
  - ✓ Mention of Scholarly Work (111/111)
  - ✓ Social/Political Advocacy (111/111)
  - ✓ Coalition Building (111/111)
  - ✓ Out of the Mouth of Academics (111/111)
  - ✓ Out of the Mouth of Activists (111/111)
  - ✓ Collective Synecdoche (111/111)
- **Analysis:** ✓ Complete
- **Visualizations:** ✓ Complete
- **Average Kappa:** **0.487** (79.4% agreement)

### ⚠️ Llama 3.3 70B - INCOMPLETE (FREE tier stalled)
- **Status:** ⏸️ PAUSED - Severe rate limiting on FREE tier
- **Model:** `meta-llama/llama-3.3-70b-instruct:free`
- **API:** OpenRouter (FREE tier)
- **Progress:** 162/999 messages (16.2%)
  - ✓ Scholar (111/111) - COMPLETE
  - ⚠️ Activist (51/111) - IN PROGRESS
  - ❌ Other codes (0/111) - NOT STARTED
- **Issue:** FREE tier has severe rate limits preventing progress
- **Options:** Switch to paid tier or abandon

---

## What Changed

### The Fix
**Before:** Models coded passages at pandas index 9-119 from `passages.csv`
**After:** Models code passages with gold standard IDs 9-119 from `gold_standard_coding.csv`

**Result:** Passages now match between model outputs and evaluation data!

### Collection Improvements
1. ✅ Unified OpenRouter API for all models
2. ✅ Automatic rate limit handling with exponential backoff
3. ✅ FREE Llama tier (no cost!)
4. ✅ Progress saving and resumption
5. ✅ Parallel collection for all models

---

## Resolution Options

### Option 1: Add Credits to OpenRouter (Recommended for completion)
**Pros:**
- Can complete all models with unified API
- Automatic rate limiting already implemented
- Progress already saved (can resume immediately)
- Consistent approach across models

**Cons:**
- Requires adding funds to account
- Link: https://openrouter.ai/settings/credits

**To Resume After Adding Credits:**
```bash
cd "/Users/taggertsmith/Desktop/LLM Deductive Coding Benchmark"

# Resume Qwen (357 messages remaining)
nohup python src/collection/run_all_openrouter.py \
  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 \
  qwen > qwen_collection.log 2>&1 &

# Resume Llama (889 messages remaining)
nohup python src/collection/run_all_openrouter.py \
  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 \
  llama > llama_collection.log 2>&1 &

# Resume Gemini (999 messages remaining)
nohup python src/collection/run_all_openrouter.py \
  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 \
  gemini > gemini_collection.log 2>&1 &
```

### Option 2: Use Native Gemini API
**Pros:**
- May have separate credit allocation
- Direct API might be faster

**Cons:**
- Would need to update collection scripts
- Different API format and error handling
- Gemini collection shows 0 progress so far

### Option 3: Analyze Partial Qwen Data Only
**Pros:**
- Can proceed immediately with 5/9 complete codes
- Bug fix already verified (κ = 0.604)
- Sufficient to demonstrate the correction

**Cons:**
- Incomplete dataset (555/999 messages for complete codes only)
- Missing 4 codes entirely
- Cannot compare across models

---

## Next Steps

### If Credits Added
- ✅ Resume all three collections with commands above
- ⏳ Monitor collections until complete (~1-2 hours more)
- ⏳ Process all results once complete
- ⏳ Run full analysis with all models
- ⏳ Generate corrected visualizations
- ⏳ Update README with real findings

### If Proceeding with Partial Data
- ⏳ Process Qwen's 5 complete codes only
- ⏳ Run analysis on available data
- ⏳ Document limitations in README
- ⏳ Plan for completing collection later

### Expected Final Results
Based on preliminary Qwen data, we expect:
- **Qwen:** κ ≈ 0.6 (confirmed!)
- **Llama:** κ ≈ 0.5-0.7 (to be determined)
- **Gemini:** κ ≈ 0.4-0.6 (to be determined)

All should be **positive** and show meaningful model performance!

---

## Monitoring Commands

```bash
# Check Qwen progress
find results/raw/output_qwen -name "message_*.txt" | wc -l

# Check Llama progress
find results/raw/output_llama -name "message_*.txt" | wc -l

# Check Gemini progress
find results/raw/output_gemini -name "message_*.txt" | wc -l

# View logs
tail -f qwen_collection.log
tail -f llama_collection.log
tail -f gemini_collection.log

# Check running processes
ps aux | grep run_all_openrouter
```

---

**Status:** ✅ QWEN & GEMINI COMPLETE - Analyzed with visualizations
**Bug Fix:** ✅ VERIFIED - Positive Kappas confirm correct alignment
**Results:** Moderate agreement (κ ≈ 0.48) for both models, ~0.20 below GPT-4
**Remaining:** Llama collection incomplete (FREE tier limitations)
