# Investigation Report: Negative Kappa Values

## Date: 2025-12-28

## Executive Summary

**CRITICAL BUG IDENTIFIED**: The negative Cohen's Kappa values for Gemini, Llama, and Qwen are caused by a fundamental data alignment error. These models are coding the WRONG passages - they're using pandas index positions from `passages.csv` instead of the actual gold standard passage IDs.

## The Problem

### What Went Wrong

The data collection scripts for Gemini, Llama, and Qwen contain this code pattern:

```python
passages = pd.read_csv("data/raw/passages.csv")
passages_include = range(9, 120)
messages = passages.loc[passages.index.isin(passages_include), 'passage']
```

This code:
1. Loads `passages.csv` (which has passages at pandas indices 0-232)
2. Selects passages at **indices** 9-119
3. Sends these to the models for coding

However, the gold standard uses a different ID system:
- `gold_standard_coding.csv` has an 'id' column ranging 0-232
- These IDs do NOT correspond to the pandas index in `passages.csv`
- The test set should use **gold standard IDs** 9-119, not pandas indices 9-119

### Evidence

#### Passage Mismatch Example (ID/Index 10):

**Pandas Index 10 in passages.csv:**
```
"W. E. B. Du Bois, the remarkable scholar, polemicist and spokesman..."
```

**Gold Standard ID 10:**
```
"When reading Plato about justice, for example, an automobile mechanic..."
```

These are completely different passages!

#### ID Distribution:

| Source | ID/Index Range | Count | Alignment |
|--------|---------------|-------|-----------|
| GPT-4 processed | 0-232 (scattered) | 111 | ✓ Correct (matches gold standard IDs) |
| Gemini processed | 9-119 (sequential) | 111 | ✗ Wrong (pandas indices) |
| Llama processed | 9-119 (sequential) | 111 | ✗ Wrong (pandas indices) |
| Qwen processed | 9-119 (sequential) | 111 | ✗ Wrong (pandas indices) |
| Gold standard | 0-232 (scattered) | 111 | Reference |

#### Verification:

When checking if ID 10 passages match:
- **GPT-4 vs Gold**: ✓ Passages match
- **Qwen vs Gold**: ✗ Completely different passages
- **Gemini vs Gold**: ✗ Completely different passages  
- **Llama vs Gold**: ✗ Completely different passages

## Why This Caused Negative Kappa

When models code passage X but are compared against gold standard for passage Y:
1. There's no semantic relationship between the passages
2. The code applications are essentially random relative to each other
3. Cohen's Kappa can go negative when agreement is worse than chance
4. Negative Kappa (-0.09 to -0.10) indicates systematic anti-correlation

The models weren't "bad" - they were coding completely different text!

## How GPT-4 Was Correct

The original GPT-4 data must have been collected using the correct passage IDs from the gold standard. The GPT-4 processed CSV contains:
- ID column with scattered values (106, 112, 57, 43, 94, etc.)
- Exact passage text matching gold standard
- Proper Kappa of 0.676

## Impact

1. **Gemini results**: INVALID - not actually testing Gemini performance
2. **Llama results**: INVALID - not actually testing Llama performance  
3. **Qwen results**: INVALID - not actually testing Qwen performance
4. **GPT-4 results**: VALID - correctly replicated
5. **All visualizations comparing models**: INVALID

## Root Cause Analysis

The bug was introduced when creating the Gemini collection workflow (likely first) and then copy-pasted to Llama and Qwen workflows. The original GPT-4 workflow correctly used gold standard IDs, but this pattern wasn't followed for the alternative models.

## Required Fixes

### Affected Files:
1. `src/collection/gemini_coding_workflow.py` - lines ~200-210
2. `src/collection/groq_coding_workflow.py` - lines ~296-298
3. `src/collection/openrouter_coding_workflow.py` - lines ~280-282

### Fix Pattern:

**Wrong (current):**
```python
passages = pd.read_csv("data/raw/passages.csv")
passages_include = range(9, 120)
messages = passages.loc[passages.index.isin(passages_include), 'passage']
```

**Correct (should be):**
```python
gold_standard = pd.read_csv("data/processed/gold_standard_coding.csv")
test_set_ids = range(9, 120)
gold_test = gold_standard[gold_standard['id'].isin(test_set_ids)]
messages = gold_test['passage']
# Also need to preserve the 'id' column for proper alignment
```

### Data to Recollect:

All Gemini, Llama, and Qwen data must be recollected with correct passage alignment:
- ~999 API calls for Qwen
- Similar for Gemini and Llama
- Will require re-running data collection scripts

## Verification Steps

After fixing:

1. ✓ Verify ID ranges match gold standard (scattered 9-119 from 0-232 range)
2. ✓ Verify passage text matches gold standard for sample IDs
3. ✓ Confirm Kappa values become positive and reasonable
4. ✓ Check that all 111 test set passages are coded
5. ✓ Regenerate all analyses and visualizations

## Lessons Learned

1. **Always verify data alignment** when replicating studies
2. **Don't assume index == ID** - check the actual data structure
3. **Test with sample passages** before full data collection
4. **Sanity check results** - negative Kappa should trigger investigation
5. **Verify against original** - our GPT-4 Kappa matched (0.676), which validated that path

## Status

- [x] Bug identified and documented
- [ ] Code fixes implemented
- [ ] Data recollection completed
- [ ] Analysis re-run with correct data
- [ ] Results validated
- [ ] Visualizations regenerated
- [ ] Documentation updated

## Next Steps

1. **IMMEDIATE**: Stop treating current results as valid
2. **PRIORITY**: Fix the data collection scripts
3. **REQUIRED**: Recollect all Gemini, Llama, and Qwen data
4. **THEN**: Rerun analysis and regenerate visualizations
5. **FINALLY**: Update README and reports with corrected findings

---

**Investigator**: Claude (AI Assistant)
**Date**: December 28, 2025
**Confidence**: 100% - Bug confirmed through multiple verification methods
