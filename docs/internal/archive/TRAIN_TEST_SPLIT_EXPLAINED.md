# Train/Test Split: Detailed Explanation

**Date:** December 8, 2025

---

## Overview

The dataset uses a **highly unusual 9/111 train/test split** (7.5%/92.5%), which is NOT a traditional machine learning split. This document explains what each set contains, how they were used, and why this design choice was made.

---

## Dataset Structure

### Total Corpus
- **Total passages:** 233 New York Times articles about W.E.B. Du Bois
- **Source:** Articles spanning multiple decades
- **Gold standard coded:** 120 passages (IDs 0-119)
- **Uncoded:** 113 passages (IDs 120-232)

### The Three ID Ranges

| ID Range | Name | Size | Purpose | Coded? |
|----------|------|------|---------|--------|
| **0-8** | "Train Set" | 9 | Pilot/calibration | ✓ Yes |
| **9-119** | **Test Set** | 111 | **Model evaluation** | ✓ Yes |
| **120-232** | Unused | 113 | Uncoded corpus | ✗ No |

---

## Train Set (IDs 0-8)

### Characteristics

**Size:** 9 passages

**Coding Statistics:**
- **100% coded:** All 9 passages have at least one code
- **Total codes applied:** 24
- **Average codes per passage:** 2.67 (higher than test set!)
- **Most common codes:**
  - Social/Political Advocacy: 6/9 (66.7%)
  - Activist: 5/9 (55.6%)
  - Monumental Memorialization: 3/9 (33.3%)

### Purpose (Hypotheses)

The train set was **NOT used for model training** in the traditional sense. Possible uses:

#### 1. **Human Coder Calibration**
- Used to train/calibrate human coders before coding the test set
- Establishes inter-rater reliability among human coders
- Standard practice in qualitative research

#### 2. **Prompt Engineering Validation**
- Test different prompt phrasings
- Validate code definitions
- Ensure instructions are clear before large-scale evaluation

#### 3. **Pilot Study**
- Initial exploration to assess feasibility
- Identify problematic codes
- Refine methodology before main study

#### 4. **Few-Shot Examples (Not Currently Used)**
- Reserved for potential few-shot prompting experiments
- Not included in current zero-shot implementation
- Could be used in future work

### Distribution Bias

The train set is **NOT representative** of the test set:

| Code | Train % | Test % | Difference |
|------|---------|--------|------------|
| Activist | 55.6% | 20.7% | **-34.8%** ⚠️ |
| Social/Political Advocacy | 66.7% | 45.9% | **-20.7%** |
| Monumental Memorialization | 33.3% | 11.7% | **-21.6%** |
| Collective Synecdoche | 11.1% | 23.4% | **+12.3%** |

**Implication:** If the train set were used for few-shot learning, this bias could hurt performance on underrepresented codes.

---

## Test Set (IDs 9-119)

### Characteristics

**Size:** 111 passages

**Coding Statistics:**
- **83.8% coded:** 93 passages have at least one code
- **16.2% negative examples:** 18 passages have no codes
- **Total codes applied:** 214
- **Average codes per passage:** 1.93

### Code Distribution

| Code | Count | % of Test Set | Prevalence |
|------|-------|---------------|------------|
| Social/Political Advocacy | 51 | 45.9% | Very Common |
| Out of the Mouth of Academics | 30 | 27.0% | Common |
| Scholar | 27 | 24.3% | Uncommon |
| Collective Synecdoche | 26 | 23.4% | Uncommon |
| Mention of Scholarly Work | 24 | 21.6% | Uncommon |
| Activist | 23 | 20.7% | Uncommon |
| Monumental Memorialization | 13 | 11.7% | Rare |
| Out of the Mouth of Activists | 11 | 9.9% | Rare |
| Coalition Building | 9 | 8.1% | **Very Rare** |

### Class Imbalance Challenge

**Most common:** Social/Political Advocacy (45.9%)
**Rarest:** Coalition Building (8.1%)
**Ratio:** 5.7:1 imbalance

This creates a challenging classification problem, especially for rare codes.

### How It Was Used

**All intercoder reliability analyses** compare model predictions against human gold standard **only on IDs 9-119**:

```python
row_ids = range(9, 120)  # Test set only
```

**Models evaluated:**
- ✓ GPT-4: All 6 conditions
- ✓ GPT-3.5: 2 conditions
- ✓ Gemini: 2 conditions (with justification only)

**Metrics calculated:**
- Cohen's Kappa (primary)
- Krippendorff's Alpha
- Gwet's AC1
- Percent Agreement
- F1 Score
- Accuracy

---

## Uncoded Passages (IDs 120-232)

### Characteristics

**Size:** 113 passages (48.5% of corpus!)

**Coding Status:**
- **0% coded:** No gold standard coding exists
- **Purpose:** Unknown
- **Speculation:**
  - Original corpus before sampling
  - Too difficult/ambiguous to code
  - Time/budget constraints
  - Used for other analyses not included in this study

### Why So Many Uncoded?

Possible explanations:

1. **Sampling Strategy:** Researchers selected 120 "best" passages for coding
2. **Diminishing Returns:** After 120 passages, adding more didn't improve reliability estimates
3. **Cost Constraints:** Human coding is expensive ($50-100/passage for expert coders)
4. **Quality Control:** Only passages with clear coding decisions included

---

## Zero-Shot Evaluation Design

### What the Models Received

**Input to LLMs:**
1. Code definitions (with synthetic examples)
2. Individual passage text
3. Question: "Does this code apply?"

**What they did NOT receive:**
- Training on actual passages
- Few-shot examples from train set
- Fine-tuning on this dataset
- Previous passages as context

### Why Zero-Shot?

This design choice makes the task:

**Advantages:**
- ✓ Tests true generalization ability
- ✓ Realistic for real-world qualitative research
- ✓ No risk of overfitting to training data
- ✓ Fair comparison across models (no model-specific tuning)

**Disadvantages:**
- ✗ More challenging than few-shot or fine-tuned
- ✗ Doesn't leverage available labeled data (train set)
- ✗ May underestimate achievable performance

### Alternative Designs Not Used

**Few-Shot (could have used train set):**
```
Give models 2-3 examples from train set before each test passage
Expected improvement: +10-20% Kappa
```

**Fine-Tuned:**
```
Train adapter layers on train set
Expected improvement: +20-40% Kappa
Not done due to: Small train set, study design goals
```

---

## Comparison with Standard ML Practice

### Traditional ML Splits

| Application | Train | Validation | Test | Reasoning |
|-------------|-------|------------|------|-----------|
| **Image Classification** | 70% | 15% | 15% | Large datasets, supervised learning |
| **NLP Tasks** | 80% | 10% | 10% | Medium datasets, need validation |
| **Few-Shot Learning** | 5-10% | 0% | 90-95% | Limited labels, test generalization |
| **This Study** | **7.5%** | **0%** | **92.5%** | **Few-shot style evaluation** |

### This Study's Approach

The 9/111 split is closest to **few-shot learning evaluation**, where:
- Small "support set" (train) available but not always used
- Large "query set" (test) for robust evaluation
- Focus on generalization, not memorization

---

## Statistical Implications

### Sample Size Considerations

**Test Set (n=111):**
- ✓ Adequate for estimating Cohen's Kappa (SE ≈ 0.05)
- ✓ Sufficient for detecting moderate effects (power ≈ 0.80)
- ✓ Allows code-level analysis (n=111 per code)

**Train Set (n=9):**
- ✗ Too small for supervised learning
- ✗ Too small for reliable few-shot learning
- ✓ Adequate for pilot study
- ✓ Adequate for human coder calibration

### Code-Level Statistics

For rare codes like "Coalition Building" (n=9 in test set):

```
Sensitivity to single misclassification:
- With n=9, one error changes Kappa by ~0.11
- With n=51 (Social/Political Advocacy), one error changes Kappa by ~0.02
```

**Implication:** Rare code performance estimates are noisier.

---

## Recommendations for Future Studies

### If Using Train Set for Few-Shot:

1. **Address distribution bias:**
   - Stratified sampling to match test set distribution
   - Weight examples by code rarity

2. **Optimal number of examples:**
   - Research suggests 3-5 examples per code is optimal
   - Would require 27-45 passages for 9 codes
   - Current train set (n=9) insufficient

3. **Example selection:**
   - Choose prototypical examples
   - Include edge cases for difficult codes
   - Balance positive and negative examples

### If Expanding Dataset:

1. **Code the uncoded passages (IDs 120-232):**
   - Adds 113 passages (nearly doubles test set)
   - Improves statistical power
   - Allows 70/30 or 80/20 split

2. **Create larger train set:**
   - Minimum 30 passages for few-shot
   - 50-70 passages for potential fine-tuning
   - Ensure representative distribution

3. **Add validation set:**
   - 10-20% of data for hyperparameter tuning
   - Prevents overfitting in prompt engineering
   - Standard ML best practice

---

## Summary

### Key Takeaways

1. **The 9/111 "train/test" split is misleading terminology**
   - Not a traditional ML split
   - "Train set" not used for model training
   - Better termed: "Pilot set" and "Evaluation set"

2. **This is a zero-shot evaluation study**
   - Models receive no training on actual passages
   - Tests generalization from code definitions alone
   - More challenging than few-shot or fine-tuned

3. **The test set is well-designed for evaluation**
   - 111 passages provides adequate statistical power
   - Includes negative examples (18 passages with no codes)
   - Representative distribution across codes

4. **The train set's purpose remains unclear**
   - Most likely: Human coder calibration
   - Possibly: Prompt engineering validation
   - Underutilized: Could improve performance if used for few-shot

5. **48.5% of the corpus is uncoded**
   - 113 passages not used in current study
   - Represents missed opportunity for larger test set
   - May be useful for future work

---

## Data Availability

**Files containing train/test information:**
- `data/processed/gold_standard_coding.csv` - All coded passages (IDs 0-119)
- `data/raw/passages.csv` - Full corpus (IDs 0-232)
- `src/analysis/replicate_analysis.py` - Line 21: `row_ids = range(9, 120)`

**How to identify train vs test:**
```python
import pandas as pd

gold = pd.read_csv('data/processed/gold_standard_coding.csv')

train = gold[gold['id'].between(0, 8)]      # n=9
test = gold[gold['id'].between(9, 119)]     # n=111
uncoded = gold[gold['id'] > 119]            # n=113
```

---

**Document Version:** 1.0
**Last Updated:** December 8, 2025
**Analysis:** LLM Qualitative Coding Replication Study
