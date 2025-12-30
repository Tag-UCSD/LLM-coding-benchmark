# LLM Benchmarking for Deductive Qualitative Coding

![Language](https://img.shields.io/badge/language-Python%20%7C%20R-blue)

Replication of an LLM-assisted qualitative coding study, extended into a multi-model benchmark for closed (deductive) coding across curated thematic analysis datasets.

## Project Overview

This repository began as a replication of the paper "Scalable Qualitative Coding with LLMs: Chain-of-Thought Reasoning Matches Human Performance in Some Hermeneutic Tasks" and evolved into a broader benchmark of LLM performance on closed, deductive qualitative coding. The work now includes:

- Replication of the original analysis using the authors' data and code.
- Extensions comparing GPT-4, GPT-3.5, Gemini 2.5 Flash-Lite, Llama 3.3 70B (via Groq), and Qwen 2.5 72B (via OpenRouter) on the same gold-standard coding task.
- Additional analyses linking model performance to code-level concreteness.
- A research agenda that continues into inductive coding on the same datasets and a parallel project on automated barrier detection in user feedback.

The primary contribution is a reproducible, end-to-end pipeline for evaluating LLMs against human expert coding in a realistic qualitative research workflow, as well as preliminary results using open and locally-run models for deductive coding compared to GPT, revealing significant performance gaps on this nuanced task.

## Methodology

### Datasets
- W.E.B. Du Bois New York Times passage corpus (233 passages total).
- Gold standard coding for 120 passages; evaluation uses the 111-passage test subset (IDs 9-119).
- 9 deductive codes spanning characterization, general themes, and canonization.

### Models Benchmarked
- GPT-4 (multiple prompting conditions).
- GPT-3.5 (per-code conditions).
- Gemini 2.5 Flash-Lite (per-code and full-codebook with justification).
- Llama 3.3 70B (Groq API, per-code with justification).
- Qwen 2.5 72B (OpenRouter API, per-code with justification).
- Mistral-Small workflow is included but not yet integrated into the core results.

### Evaluation
- Intercoder reliability: Cohen's Kappa (primary), Krippendorff's Alpha, Gwet's AC1, percent agreement.
- Classification metrics: F1 and accuracy (when available).
- Prompting conditions: per-code vs full-codebook, with and without justification.

### Deductive Qualitative Coding (Closed Coding)
Closed coding applies a fixed, predefined codebook to text passages, evaluating whether each code applies. In this project, LLM outputs are compared directly to human gold-standard labels to assess reliability and usefulness for qualitative research workflows.

## Repository Structure

The current repository is organized by workflow stage:

- `data/processed/gold_standard_coding.csv`, `data/raw/passages.csv` - source data and gold labels.
- `results/raw/output_original/` - original GPT outputs from the replication package.
- `results/raw/output_gemini/`, `results/raw/output_llama/`, `results/raw/output_qwen/` - model-specific raw outputs and processed CSVs.
- `results/outputs/` - consolidated results tables.
- `results/figures/` - publication-ready figures.
- `src/analysis/replicate_analysis.py` - core replication and metric computation.
- `src/processing/process_gemini_results.py`, `src/processing/process_llama_results.py`, `src/processing/process_qwen_results.py` - parsing raw model responses.
- `src/analysis/analyze_gemini_results.py`, `src/analysis/analyze_llama_results.py`, `src/analysis/analyze_qwen_results.py` - model comparisons against gold standard.
- `src/visualization/create_visualizations.R`, `src/visualization/create_gemini_visualizations.R`, `src/visualization/create_threeway_visualizations.R`, `src/visualization/create_fourway_visualizations.R` - figure generation.
- `docs/reports/REPLICATION_REPORT.md`, `docs/reports/GEMINI_ANALYSIS_REPORT.md` - narrative reports.

## Key Findings (High Level)

### ⚠️ Critical Bug Fix (December 2025)

**Original Issue**: Initial results showed negative Kappa values (κ ≈ -0.10) for all alternative models (Gemini, Llama, Qwen), indicating worse-than-random performance.

**Root Cause**: Data alignment bug in collection scripts. Models were coding passages from pandas index positions (9-119 sequential) instead of using gold standard IDs (9-119 scattered across 0-232 range). This caused models to code **completely different passages** than the gold standard.

**Resolution**: Fixed passage loading to use `gold_standard_coding.csv` with correct IDs. All data recollected with corrected scripts.

**Impact**: After fix, Kappa values increased from negative to moderate positive (Δκ ≈ +0.58), confirming bug resolution.

### Model Performance (Average Cohen's Kappa) - CORRECTED

**Fully Tested:**
1. **GPT-4** (per-code with justification): **κ ≈ 0.68** ⭐ **BEST** *(from original study)*
2. **Gemini 2.5 Flash-Lite** (per-code with justification): **κ = 0.487** (79.4% agreement)
3. **Qwen 2.5 72B** (per-code with justification): **κ = 0.477** (87.5% agreement)

**Partially Tested:**
4. **Llama 3.3 70B** (per-code with justification): Collection incomplete (FREE tier rate limits)

### Key Observations

- **GPT-4 remains the strongest performer** on this nuanced qualitative coding task (κ ≈ 0.68).
- **Gemini and Qwen show moderate agreement** with gold standard (κ ≈ 0.48), significantly better than random but below GPT-4.
- **Very similar performance** between Gemini (κ = 0.487) and Qwen (κ = 0.477), with Gemini slightly ahead in Kappa but Qwen showing higher percent agreement (87.5% vs 79.4%).
- **Both models excel** at Monumental Memorialization (κ ≈ 0.96 for both) but struggle with nuanced codes like "Out of the Mouth of Activists" (κ < 0.21).
- **Model-specific strengths**: Qwen better at Collective Synecdoche (κ = 0.749 vs 0.272); Gemini better at Coalition Building (κ = 0.199 vs 0.000).
- **Code difficulty varies widely**; attribution-style codes remain the hardest across all models.
- Per-code with justification (chain-of-thought) continues to be the most effective prompt strategy.

See `RESULTS_SUMMARY.md` for complete analysis and `results/figures/` for visualizations.

## Getting Started

### Requirements
- Python 3.9+ with: `pandas`, `numpy`, `scikit-learn`, `krippendorff`, `pycm`, `google-generativeai`, `groq`, `openai`, `huggingface_hub`
- R 4.2+ with: `ggplot2`, `dplyr`, `tidyr`, `scales`, `viridis`

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
R -e "install.packages(c('ggplot2','dplyr','tidyr','scales','viridis'))"
```

## Usage

### Replicate the original paper analysis
```bash
python src/analysis/replicate_analysis.py
Rscript src/visualization/create_visualizations.R
```

### Process and analyze Gemini outputs
```bash
python src/processing/process_gemini_results.py
python src/analysis/analyze_gemini_results.py
Rscript src/visualization/create_gemini_visualizations.R
```

### Process and analyze Llama outputs
```bash
python src/processing/process_llama_results.py
python src/analysis/analyze_llama_results.py
Rscript src/visualization/create_threeway_visualizations.R
```

### Process and analyze Qwen outputs
```bash
python src/processing/process_qwen_results.py
python src/analysis/analyze_qwen_results.py
```

### Generate Qwen vs Gemini visualizations
```bash
Rscript src/visualization/create_qwen_gemini_visualizations.R
```

### Monitor collection progress
```bash
python check_progress.py
# or for quick status:
./quick_status.sh
```

### Data collection (API keys required)
All models now use OpenRouter unified API for simplified collection:
```bash
# Collect data for specific model
python src/collection/run_all_openrouter.py YOUR_OPENROUTER_API_KEY qwen
python src/collection/run_all_openrouter.py YOUR_OPENROUTER_API_KEY gemini
python src/collection/run_all_openrouter.py YOUR_OPENROUTER_API_KEY llama

# Or collect all models in parallel
for model in qwen gemini llama; do
  nohup python src/collection/run_all_openrouter.py YOUR_OPENROUTER_API_KEY $model > ${model}_collection.log 2>&1 &
done
```

**Features:**
- Automatic rate limit handling with exponential backoff
- Progress saving and resumption capability
- Correct passage alignment with gold standard IDs
- Unified API key for all models

## Citation

If you use this repository, please cite it and the original paper:

```bibtex
@misc{llm_qual_coding_benchmark,
  title = {LLM Benchmarking for Deductive Qualitative Coding},
  author = {Smith, Taggert},
  year = {2025},
  howpublished = {GitHub repository},
  note = {URL to be added}
}
```

For the original study, see [Dunivin (2025)][dunivin_link].

## Future Work

- Continuation of these experiments using other open-source models. 
- Robust error analysis and failure mode taxonomy based on other psycholinguistic norms in addition to concreteness.
- Parallel project on automated detection and classification of barriers in user feedback.
- (collaboration with GPT-Scientist team) Inductive (open) coding experiments using the same datasets I collected.

## License and Contact

- License: MIT.
- Contact: tds002@ucsd.edu.

## References

Dunivin, Z.O. Scaling hermeneutics: a guide to qualitative coding with LLMs for reflexive content analysis. EPJ Data Sci. 14, 28 (2025). https://doi.org/10.1140/epjds/s13688-025-00548-8

[dunivin_link]: https://doi.org/10.1140/epjds/s13688-025-00548-8
