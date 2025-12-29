# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an LLM benchmarking project for deductive qualitative coding, replicating and extending "Scalable Qualitative Coding with LLMs" (Dunivin, 2025). The project evaluates multiple LLMs (GPT-4, GPT-3.5, Gemini 2.5 Flash-Lite, Llama 3.3 70B) on closed coding tasks using W.E.B. Du Bois New York Times passages with 9 predefined codes.

**Key Domain Concepts:**
- **Deductive/Closed Coding:** Applying a fixed, predefined codebook to text passages
- **Intercoder Reliability:** Agreement between coders (LLM vs human gold standard), measured via Cohen's Kappa, Krippendorff's Alpha, Gwet's AC1, and percent agreement
- **Prompting Conditions:** Per-code vs full-codebook, with/without justification (chain-of-thought)
- **Test Set:** Passages with IDs 9-119 (111 passages total) from `data/processed/gold_standard_coding.csv`

## Common Commands

### Python Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### R Environment Setup
```bash
R -e "install.packages(c('ggplot2','dplyr','tidyr','scales','viridis'))"
```

### Core Analysis Workflows

**Replicate original GPT analysis:**
```bash
python src/analysis/replicate_analysis.py
Rscript src/visualization/create_visualizations.R
```

**Process and analyze Gemini results:**
```bash
python src/processing/process_gemini_results.py
python src/analysis/analyze_gemini_results.py
Rscript src/visualization/create_gemini_visualizations.R
```

**Process and analyze Llama results:**
```bash
python src/processing/process_llama_results.py
python src/analysis/analyze_llama_results.py
Rscript src/visualization/create_threeway_visualizations.R
```

**Multi-model comparison:**
```bash
Rscript src/visualization/create_threeway_visualizations.R
```

### Data Collection (requires API keys)
```bash
python src/collection/resume_gemini.py YOUR_GEMINI_API_KEY
python src/collection/resume_llama.py YOUR_GROQ_API_KEY
```

**Note:** Collection scripts automatically skip already-coded passages and resume from where they left off.

## Code Architecture

### Data Pipeline Flow

The project follows a three-stage pipeline:

1. **Collection (`src/collection/`)** → Raw API responses saved to `results/raw/output_<model>/`
2. **Processing (`src/processing/`)** → Parse responses into CSVs matching gold standard format
3. **Analysis (`src/analysis/`)** → Calculate intercoder reliability metrics, compare to gold standard
4. **Visualization (`src/visualization/`)** → Generate figures in `results/figures/`

### Module Organization

**`src/collection/`**
- `gemini_coding_workflow.py`, `groq_coding_workflow.py`: Core API interaction logic for each model
- `resume_gemini.py`, `resume_llama.py`: Entry points for data collection with automatic resumption
- Collection scripts use `codes_full` definitions (9 codes with title, category, definition, examples)

**`src/processing/`**
- `process_gemini_results.py`, `process_llama_results.py`: Parse raw API responses into tabular format
- Extract binary (0/1) code assignments per passage
- Handle two response formats: per-code (separate API calls per code) and full-codebook (all codes in one call)
- Output CSVs must match gold standard structure: rows = passage IDs, columns = code names

**`src/analysis/`**
- `replicate_analysis.py`: Core analysis module with reusable functions:
  - `load_and_align_data()`: Aligns multiple CSV files by passage ID, filters to test set (IDs 9-119)
  - `calculate_intercoder_reliability()`: Computes Cohen's Kappa, Krippendorff's Alpha, Gwet's AC1, percent agreement
  - `get_ir_report_df()`: Generates summary tables across all codes and conditions
- `analyze_gemini_results.py`, `analyze_llama_results.py`: Model-specific analysis importing functions from `replicate_analysis.py`
- `analyze_concreteness*.py`: Experimental analyses linking code difficulty to psycholinguistic concreteness

**`src/visualization/`**
- R scripts generate three core visualizations:
  1. Heatmap of Cohen's Kappa by code and condition
  2. Bar plot of average performance across conditions
  3. Bar plot of code difficulty (averaged across conditions)
- Model-specific scripts: `create_gemini_visualizations.R`, `create_threeway_visualizations.R`
- All scripts read from `results/outputs/*.csv` and write PNG figures to `results/figures/`

### Data Files

**Key data locations:**
- `data/raw/passages.csv`: W.E.B. Du Bois text passages (233 total)
- `data/processed/gold_standard_coding.csv`: Human expert coding (111 test passages × 9 codes)
- `data/processed/concreteness.xlsx`: Psycholinguistic norms for experimental analyses
- `results/raw/output_original/`: Original GPT outputs from replication package
- `results/raw/output_gemini/`, `results/raw/output_llama/`: Model-specific raw API responses
- `results/outputs/`: Consolidated CSV results tables
- `results/figures/`: Publication-ready PNG visualizations

**Important:** The test set always uses passage IDs 9-119 (111 passages). This is hardcoded in `row_ids = range(9, 120)` across analysis scripts.

### Code Definitions

The 9 deductive codes are defined in `codes_full` (see `src/collection/gemini_coding_workflow.py:25-80`):

**Characterization:** Scholar, Activist
**General Themes:** Monumental Memorialization, Mention of Scholarly Work, Social/Political Advocacy
**Canonization:** Coalition Building, Out of the Mouth of Academics, Out of the Mouth of Activists, Collective Synecdoche

Each code has: `title`, `category`, `definition` (detailed instructions), `examples` (sample passages).

### Prompting Conditions

Two orthogonal experimental dimensions:
1. **Per-code vs Full-codebook:** Whether each code is evaluated in a separate API call or all codes evaluated together
2. **With/without justification:** Whether the prompt requests chain-of-thought reasoning before the binary decision

Directory naming convention: `<condition>_t=<temperature>_top_p=<top_p>_model=<model>`
Example: `per-code-with-justification_t=0_top_p=1_model=gemini`

### Analysis Functions

All analysis scripts reuse functions from `replicate_analysis.py`:

- **`load_and_align_data(files, ids, id_column=None)`**: Loads CSVs, filters to specified passage IDs, aligns by index, fills NaN with 0
- **`calculate_intercoder_reliability(y_true, y_pred)`**: Returns dict with `cohen_kappa`, `krippendorff_alpha`, `gwet_ac1`, `percent_agreement`
- **`get_ir_report_df(aligned_df, coded_columns, rater1_idx, rater2_idx)`**: Loops over codes, calculates metrics, returns summary DataFrame

When adding new model analyses, import and reuse these functions rather than reimplementing.

### Dependencies

**Python:** pandas, numpy, scikit-learn, krippendorff, pycm, google-generativeai, groq, huggingface_hub
**R:** ggplot2, dplyr, tidyr, scales, viridis

All Python dependencies are in `requirements.txt`. R packages must be installed manually.

## Development Patterns

### Adding a New Model

1. Create collection workflow in `src/collection/<model>_coding_workflow.py` following `gemini_coding_workflow.py` pattern
2. Create resumption script `src/collection/resume_<model>.py`
3. Run collection to generate `results/raw/output_<model>/`
4. Create `src/processing/process_<model>_results.py` to parse responses into CSV matching gold standard format
5. Create `src/analysis/analyze_<model>_results.py` importing functions from `replicate_analysis.py`
6. Update or create visualization script in `src/visualization/`

### Response Parsing Requirements

Model response parsers must:
- Extract binary (0/1) assignments for each code
- Handle both per-code (separate files per code) and full-codebook (single file with all codes) formats
- Output CSV with columns matching `coded_columns` from `replicate_analysis.py:14-18`
- Use passage ID as index (integers 9-119)
- Save processed CSV to `results/raw/output_<model>/`

### Statistical Reporting

All metrics should be calculated for each code individually and averaged across codes. The standard output format is a DataFrame with columns:
- `Code`: Code name or "Average"
- `Gold Standard Count`: Number of passages coded 1 in gold standard
- One column per condition with Cohen's Kappa values

See `results/outputs/intercoder_reliability_results.csv` for reference format.

## Testing Changes

When modifying analysis or processing code:
1. Run on original GPT data first to verify no regressions
2. Compare output CSVs and metrics to existing results in `results/outputs/`
3. Regenerate visualizations and check against existing PNGs in `results/figures/`
4. For new models, sanity-check that Kappa values are in reasonable range (-1 to 1, typically 0.2-0.8 for this task)

## Notes

- The repository includes Mistral workflow code but it's not yet integrated into core results pipeline
- The project uses temperature=0 and top_p=1 for all model calls to ensure reproducibility
- Concreteness analyses (`analyze_concreteness*.py`) are experimental extensions linking code difficulty to psycholinguistic norms
- All paths should be relative to repository root; scripts assume they're run from root directory
