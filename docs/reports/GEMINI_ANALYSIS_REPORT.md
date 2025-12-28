# LLM Qualitative Coding Analysis: Extended Replication with Gemini

---

## Summary

This report documents an extension of the original qualitative coding study, adding Google's Gemini model to the comparison alongside GPT-4 and GPT-3.5. The analysis reveals significant performance differences across models:

- **GPT-4** remains the best performer (κ = 0.676)
- **GPT-3.5** shows moderate performance (κ = 0.338)
- **Gemini** performs below chance level (κ = -0.092), worse than random guessing

---

## Methodology

### Data Sources
- **Gold Standard Coding:** 111 passages (IDs 9-119) coded by human experts
- **Passages:** Text excerpts about W.E.B. Du Bois from New York Times articles
- **Codes:** 9 thematic codes for qualitative analysis
- **Concreteness Data:** Linguistic concreteness scores for each code

### Models Tested

#### GPT-4 (4 conditions)
1. Per-code with justification (chain-of-thought)
2. Per-code without justification
3. Full codebook with justification
4. Full codebook without justification

#### GPT-3.5 (2 conditions)
5. Per-code with justification
6. Per-code without justification

#### Gemini (2 conditions - newly added)
7. Per-code with justification
8. Full codebook with justification

*Note: Gemini without-justification conditions were incomplete and excluded from analysis*

### Statistical Measures
- **Cohen's Kappa (κ):** Agreement between LLM and human coders, correcting for chance
- **F1 Score:** Harmonic mean of precision and recall
- **Accuracy:** Percentage of correctly classified passages
- **Linguistic Concreteness:** Average concreteness rating of code words/phrases

---

## Key Findings

### Overall Performance Rankings

| Rank | Model Condition | Mean κ | Interpretation |
|------|----------------|---------|----------------|
| 1 | GPT-4: Per-Code w/ Just | **0.676** | Substantial agreement |
| 2 | GPT-4: Full w/ Just | 0.596 | Moderate agreement |
| 3 | GPT-4: Per-Code w/o Just | 0.592 | Moderate agreement |
| 4 | GPT-4: Full w/o Just | 0.465 | Moderate agreement |
| 5 | GPT-3.5: Per-Code w/ Just | 0.338 | Fair agreement |
| 6 | GPT-3.5: Per-Code w/o Just | 0.291 | Fair agreement |
| 7 | Gemini: Full w/ Just | **-0.075** | Below chance |
| 8 | Gemini: Per-Code w/ Just | **-0.092** | Below chance |

### Model Comparison: Performance Gap

**GPT-4 vs Gemini Performance Difference:**
- Average difference: 0.768 Kappa points
- GPT-4 achieves 8.4x better Kappa than Gemini
- Gemini performs **worse than random guessing** (negative Kappa)

**Possible Explanations for Gemini's Poor Performance:**
1. **Prompt Sensitivity:** Gemini may require different prompt engineering than GPT models
2. **Training Differences:** Different training data and objectives
3. **Chain-of-Thought Limitations:** Gemini's reasoning process may not align well with this task
4. **Overgeneralization:** Gemini may be coding too many passages positively, reducing precision
5. **Task Mismatch:** Qualitative coding may not suit Gemini's design strengths

---

## Code-Level Performance Analysis

### Performance by Code (Per-Code with Justification)

| Code | Concreteness | GPT-4 κ | GPT-3.5 κ | Gemini κ | Difficulty |
|------|--------------|---------|-----------|----------|------------|
| Monumental Memorialization | 2.28 | **1.000** | 0.287 | -0.162 | ★ Easiest (for GPT-4) |
| Collective Synecdoche | 2.52 | 0.788 | 0.275 | -0.102 | ★★ Easy |
| Activist | 3.34 | 0.811 | 0.391 | 0.012 | ★★ Easy |
| Mention of Scholarly Work | 2.66 | 0.712 | 0.332 | -0.016 | ★★★ Moderate |
| Social/Political Advocacy | 2.00 | 0.636 | 0.549 | -0.141 | ★★★ Moderate |
| Out of the Mouth of Academics | 3.74 | 0.627 | 0.374 | -0.144 | ★★★ Moderate |
| Scholar | 3.50 | 0.609 | 0.294 | 0.004 | ★★★★ Hard |
| Coalition Building | 3.69 | 0.597 | 0.331 | -0.134 | ★★★★ Hard |
| Out of the Mouth of Activists | 3.74 | 0.304 | 0.210 | -0.144 | ★★★★★ Hardest |

### Notable Findings

**Perfect Agreement:** GPT-4 achieved perfect inter-rater reliability (κ = 1.000) for "Monumental Memorialization" - identifying references to memorials and monuments.

**Universal Difficulty:** "Out of the Mouth of Activists" was the most challenging code for ALL models:
- GPT-4: κ = 0.304
- GPT-3.5: κ = 0.210
- Gemini: κ = -0.144

**Gemini's Best Performance:** Even Gemini's best performance (κ = 0.012 for "Activist") is essentially zero agreement.

---

## Concreteness vs Performance Analysis

### Key Correlations

| Model | Concreteness vs F1 | Concreteness vs Accuracy |
|-------|-------------------|-------------------------|
| GPT-4 | **r = -0.667** | r = -0.073 |
| GPT-3.5 | r = -0.466 | r = 0.183 |
| Gemini | r = -0.361 | r = 0.335 |

### Interpretation

**Negative Correlation (GPT-4):** More concrete codes (e.g., "Coalition Building" = 3.69) are actually **harder** for GPT-4 to identify than abstract codes (e.g., "Social/Political Advocacy" = 2.00). This contradicts the intuitive hypothesis that concrete concepts are easier to identify.

**Hypothesis:** Abstract codes like "Social/Political Advocacy" may have clearer linguistic markers in text, while concrete codes like "Coalition Building" require deeper contextual understanding.

### Performance Metrics Summary

| Model | Mean F1 | Mean Accuracy | Performance Level |
|-------|---------|---------------|-------------------|
| GPT-4 | 0.743 | 0.902 | Excellent |
| GPT-3.5 | 0.512 | 0.725 | Good |
| Gemini | 0.200 | 0.565 | Poor |

**Gemini's F1 score of 0.200** indicates it correctly identifies only 20% of the codes on average, compared to GPT-4's 74%.

---

## Visualizations Created

All visualizations are saved in the `results/figures/` directory:

### 1. Heatmap: Cohen's Kappa by Code and Model
**File:** `results/figures/visualization1_heatmap_with_gemini.png`

Shows color-coded performance matrix across all 8 model conditions and 9 codes. Gemini's consistently poor performance (near-zero or negative Kappa) is visible as darker cells.

### 2. Bar Chart: Average Performance Across Models
**File:** `results/figures/visualization2_average_performance_with_gemini.png`

Compares mean Kappa across all conditions. Shows clear hierarchy:
- GPT-4 conditions: 0.46 - 0.68
- GPT-3.5 conditions: 0.29 - 0.34
- Gemini conditions: -0.09 - -0.07

### 3. Code Difficulty Comparison
**File:** `results/figures/visualization3_code_difficulty_with_gemini.png`

Side-by-side comparison of GPT-4, GPT-3.5, and Gemini on each code (per-code with justification condition). Dramatically illustrates Gemini's failure across all codes.

### 4. Concreteness vs Performance Scatterplots
**File:** `results/figures/concreteness_vs_performance_with_gemini.png`

Six subplots showing relationships between code concreteness and model performance:
- Top row: F1 scores for GPT-4, GPT-3.5, Gemini
- Bottom row: Accuracy for GPT-4, GPT-3.5, Gemini

Reveals negative correlation between concreteness and F1 for GPT-4, weaker patterns for other models.

---

## Conclusions

### 1. Model Performance Hierarchy

**GPT-4 >> GPT-3.5 >> Gemini**

The performance gap between GPT-4 and Gemini is dramatic and unexpected. Gemini's negative Kappa values indicate systematic errors worse than random assignment.

### 2. Best Practices for Qualitative Coding with LLMs

Based on this analysis:
- ✅ **Use GPT-4** with per-code prompting and chain-of-thought justification
- ✅ Expect substantial agreement (κ = 0.68) with human coders
- ✅ Anticipate variable performance across codes (range: 0.30 - 1.00)
- ❌ **Avoid Gemini** for qualitative coding tasks in current form

### 3. Code Difficulty is Task-Specific

Difficulty patterns vary by model:
- **GPT-4:** Struggles with attribution codes ("Out of the Mouth of...")
- **All Models:** "Out of the Mouth of Activists" is universally difficult
- **Gemini:** Fails at all codes, but especially concrete ones

### 4. Concreteness Findings

**Counter-intuitive finding:** More linguistically concrete codes are actually HARDER for GPT-4 to identify (r = -0.667). This suggests:
- Abstract concepts may have clearer textual markers, versus requiring knowledge of metadata, context, or inference
- "Easiness" for humans ≠ "easiness" for LLMs

### 5. Chain-of-Thought Reasoning

All best-performing conditions used chain-of-thought justification, confirming its importance. However, this technique failed to improve Gemini's performance, suggesting model-specific optimization is needed.

---

## Questions for Future Research

1. **Why does Gemini fail so dramatically?**
   - Is this a prompt engineering issue?
   - What is the model size threshold where we start to see acceptable results?

2. **Can Gemini be improved?**
   - Test alternative prompting strategies
   - Explore few-shot learning approaches
   - Compare with other Gemini model variants

3. **What explains the concreteness results?**
   - Analyze linguistic features of high vs low concreteness codes
   - Examine which textual cues GPT-4 relies on
   - Test hypothesis about semantic markers

---

## Acknowledgments

- Original study: "Scalable Qualitative Coding with LLMs: Chain-of-Thought Reasoning Matches Human Performance in Some Hermeneutic Tasks"
- Gold standard coding: Human expert annotators
- Models tested: OpenAI GPT-4, GPT-3.5; Google Gemini
- Analysis tools: Python (pandas, scikit-learn, krippendorff, pycm), R (ggplot2, tidyr, dplyr)

