# LLM Benchmarking for Deductive Qualitative Coding

![Language](https://img.shields.io/badge/language-Python%20%7C%20R-blue)

Replication of an LLM-assisted qualitative coding study, extended into a multi-model benchmark for closed (deductive) coding across curated thematic analysis datasets.

## Project Overview

This repository began as a replication of the paper "Scalable Qualitative Coding with LLMs: Chain-of-Thought Reasoning Matches Human Performance in Some Hermeneutic Tasks" and evolved into a broader benchmark of LLM performance on closed, deductive qualitative coding. The work now includes:

- Replication of the original analysis using the authors' data and code, validating the reported best prompting structure ("per-code, with justification")
- Extensions comparing human-LLM agreement GPT-4, GPT-3.5, Gemini 2.5 Flash-Lite, Llama 3.3 70B, and Qwen 2.5 72B (via OpenRouter) on the same gold-standard coding task.
- Additional failure mode analyses linking model performance to code-level concreteness and other psycholinguistic measures.

The primary contribution is a reproducible, end-to-end pipeline for evaluating LLMs against human expert coding in a realistic qualitative research workflow, as well as preliminary results using open and locally-run models for deductive coding compared to GPT, which has been used overwhelmingly in the prior research on deductive LLM coding and text classification. These contributions are most immediately useful to qualitative researchers seeking to scale their coding methodology to large datasets, after manually developing a codebook based on a subset.

This work will be incorporated into the next iteration of the [GPT-Scientist][gpts_link] toolkit, and informs an ongoing project involving automatic detection of barriers to user engagement with a digital health app.

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
- Intercoder reliability: Cohen's Kappa, Krippendorff's Alpha, Gwet's AC1, percent agreement.
- Classification metrics: F1 and accuracy (when available).
- Prompting conditions: per-code vs full-codebook, with and without justification.

### Deductive Qualitative Coding ("Closed Coding")
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

## Preliminary Findings

### Model Performance (Average Cohen's Kappa) 

**Four-Model Comparison (Per-Code with Justification):**

| Rank | Model | Average κ | Interpretation | Gap from GPT-4 |
|------|-------|-----------|----------------|----------------|
| 1 | **GPT-4** | **0.676** | **Substantial agreement** | - |
| 2 | **Gemini 2.5 Flash-Lite** | **0.487** | Moderate agreement | -0.189 |
| 3 | **Qwen 2.5 72B** | **0.477** | Moderate agreement | -0.199 |
| 4 | **GPT-3.5** | **0.338** | Fair agreement | -0.338 |

**Incomplete:**
- **Llama 3.3 70B**: Collection incomplete (16.2%, FREE tier rate limits)

### Key Observations

- **GPT-4 achieves best performance on ALL 9 codes** including perfect agreement (κ = 1.0) on Monumental Memorialization.
- **Gemini and Qwen show very similar moderate agreement** (κ ≈ 0.48), performing ~70% as effectively as GPT-4.
- **GPT-3.5 significantly underperforms** all other models (κ = 0.338), demonstrating the importance of model scale for nuanced qualitative tasks.
- **Low-budget viability**: Both Gemini and Qwen are viable for cost-sensitive applications, with ~0.20 Kappa point gap from GPT-4.
- **Code difficulty varies widely**: Easiest code for all models (Monumental, avg κ = 0.918) vs hardest code (Out of Mouth Activists, avg κ = 0.185).
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
- Unified API key for all models (via openrouter)

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
