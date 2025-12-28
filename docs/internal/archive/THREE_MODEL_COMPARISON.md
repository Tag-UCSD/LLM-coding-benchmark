# Three-Model LLM Comparison for Qualitative Coding

## Overview

This project compares three language models on qualitative coding of W.E.B. Du Bois news passages:

| Model | Type | Provider | Cost | Status |
|-------|------|----------|------|--------|
| **GPT-4** | Proprietary | OpenAI | ~$15-20 | ✅ Complete (κ = 0.676) |
| **Gemini 2.5 Flash-Lite** | Proprietary | Google | Free | 🔄 Running (62% done) |
| **Llama 3.1 70B** | Open-source | Meta/Groq | Free | ⏳ Ready to start |

## Quick Start

### 1. Gemini (Currently Running)

Gemini 2.5 Flash-Lite is already running. Check progress:

```bash
cd "/path/to/repo"
python src/collection/monitor_progress.py
```

### 2. Llama via Groq (Ready to Start)

**Get a FREE Groq API key:**
- Go to: https://console.groq.com
- Sign up (no credit card required)
- Create an API key (starts with `gsk_...`)

**Run Llama coding:**
```bash
cd "/path/to/repo"
python - << 'PY'
import sys
sys.path.append("src/collection")
from groq_coding_workflow import run_per_code_llama
run_per_code_llama("YOUR_GROQ_API_KEY")
PY
```

Expected time: **10-15 minutes** (Groq is extremely fast)

## What Gets Compared

### Task
Apply 9 qualitative codes to 111 news passages about W.E.B. Du Bois

### Codes
1. **Characterization**: Scholar, Activist
2. **General Themes**: Monumental Memorialization, Mention of Scholarly Work, Social/Political Advocacy
3. **Canonization**: Coalition Building, Out of the Mouth of Academics, Out of the Mouth of Activists, Collective Synecdoche

### Approach
**Per-code with justification** - The best performing method from the original paper:
- Each code is applied separately (9 passes per passage = 999 API calls)
- Model provides chain-of-thought justification before applying code
- Temperature = 0 for reproducibility

### Evaluation Metrics
- **Cohen's Kappa** (primary metric)
- Krippendorff's Alpha
- Gwet's AC1
- Percent Agreement

## Timeline

### Gemini
- ⏱ **Started**: December 2, 2024 ~21:00 PST
- 📊 **Progress**: 62% complete (621/999 calls)
- ⏰ **ETA**: ~50 minutes remaining
- ⚡ **Speed**: ~1 call/second

### Llama (Once Started)
- ⏱ **Duration**: 10-15 minutes
- ⚡ **Speed**: ~2-3 calls/second (Groq is VERY fast)
- 🎯 **Can run in parallel** with Gemini

### Total Timeline
Both models should complete within **1 hour** from now.

## Processing & Analysis

Once both Gemini and Llama complete, the automated analysis will:

### 1. Process Responses (5 minutes)
```bash
# Process Gemini
python src/processing/process_gemini_results.py

# Process Llama
python src/processing/process_llama_results.py
```

### 2. Calculate Metrics (5 minutes)
```bash
# Analyze Gemini
python src/analysis/analyze_gemini_results.py

# Analyze Llama
python src/analysis/analyze_llama_results.py
```

### 3. Create Visualizations (3 minutes)
```bash
# Individual comparisons
Rscript src/visualization/create_gemini_visualizations.R

# Three-way comparison
Rscript src/visualization/create_threeway_visualizations.R
```

**Outputs:**
- `results/figures/threeway_kappa_by_code.png` - Bar chart comparing all 3 models by code
- `results/figures/threeway_average_kappa.png` - Average performance comparison
- `results/figures/threeway_heatmap.png` - Heatmap showing performance across codes
- `results/figures/threeway_difference_from_gpt4.png` - How Gemini and Llama differ from GPT-4

## Research Questions

### Performance
1. How does each model compare to human expert coding (gold standard)?
2. Which model achieves the highest Cohen's Kappa?
3. Which codes are easiest/hardest for each model?

### Cost-Effectiveness
4. Is the free Gemini comparable to paid GPT-4?
5. Does open-source Llama match proprietary models?
6. What's the cost-quality tradeoff for each model?

### Practical Implications
7. Which model should researchers use for qualitative coding?
8. Does model choice depend on code type or complexity?
9. Can open-source models replace proprietary ones for this task?

## Model Details

### GPT-4 (Baseline)
- **Parameters**: Unknown (estimated 1.5T+)
- **Access**: OpenAI API (paid)
- **Cost**: ~$15-20 for 999 calls
- **Speed**: Moderate
- **Performance**: κ = 0.676

### Gemini 2.5 Flash-Lite
- **Parameters**: Unknown
- **Access**: Google AI API (free tier)
- **Cost**: Free (separate quota from Pro)
- **Speed**: Fast (~1 call/sec)
- **Performance**: TBD

### Llama 3.1 70B Versatile
- **Parameters**: 70 billion
- **Access**: Groq API (free tier)
- **Cost**: Free
- **Speed**: Extremely fast (~2-3 calls/sec)
- **Performance**: TBD
- **Open-source**: Yes (Meta license)

## Expected Outcomes

Based on existing benchmarks:

**Hypothesis 1**: GPT-4 will have highest Kappa
- Most expensive
- Most parameters
- Best at instruction following

**Hypothesis 2**: Llama will be competitive
- 70B parameters is substantial
- Groq's optimized inference
- Recent SOTA open-source model

**Hypothesis 3**: Gemini will fall between
- Free tier model (lighter weight)
- But Google's latest architecture
- Good for cost-effectiveness

**We'll know in ~1 hour!**

## Files Created

### Workflow Scripts
- `src/collection/groq_coding_workflow.py` - Llama coding via Groq API
- `src/collection/gemini_coding_workflow.py` - Gemini coding (already exists)

### Processing Scripts
- `src/processing/process_llama_results.py` - Extract codes from Llama responses
- `src/processing/process_gemini_results.py` - Extract codes from Gemini responses

### Analysis Scripts
- `src/analysis/analyze_llama_results.py` - Calculate Llama metrics
- `src/analysis/analyze_gemini_results.py` - Calculate Gemini metrics

### Visualization Scripts
- `src/visualization/create_threeway_visualizations.R` - Three-way comparison plots

### Documentation
- `docs/setup/LLAMA_SETUP.md` - Llama/Groq setup guide
- `docs/setup/GEMINI_SETUP_GUIDE.md` - Gemini setup guide
- `docs/reports/THREE_MODEL_COMPARISON.md` - This file

## Next Steps

1. **Get Groq API key** from https://console.groq.com
2. **Start Llama coding** (provide key when ready)
3. **Wait for both to complete** (~50 min for Gemini + 15 min for Llama)
4. **Run automated analysis** (I'll do this when both complete)
5. **Review three-way comparison** (visualizations + report)

## Contact & Support

All code is open-source and reproducible. See individual setup guides for troubleshooting:
- Gemini issues → `GEMINI_SETUP_GUIDE.md`
- Llama issues → `LLAMA_SETUP.md`
