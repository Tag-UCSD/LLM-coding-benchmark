# Mistral-Small Coding Setup

## Quick Start

1. **Get a HuggingFace API Token** (free):
   - Go to: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name it anything (e.g., "qualitative-coding")
   - Copy the token

2. **Run the Mistral coding**:
   ```bash
   cd "/path/to/repo"
   python -c "
   import sys
   sys.path.append("src/collection")
   from mistral_coding_workflow import run_per_code_mistral
   run_per_code_mistral('YOUR_HF_TOKEN_HERE')
   "
   ```

## What This Does

- Uses **Mistral-Small-Instruct-2409** (open-source)
- Runs the **per-code with justification** approach
- Makes ~999 API calls (same as Gemini)
- **FREE** with HuggingFace token
- Results comparable to GPT-4 and Gemini

## Three-Way Comparison

After both Gemini and Mistral complete, you'll have:

| Model | Type | Cost | Performance |
|-------|------|------|-------------|
| GPT-4 | Proprietary | ~$15-20 | κ = 0.676 (baseline) |
| Gemini 2.5 Flash-Lite | Proprietary | Free tier | κ = ??? (running) |
| Mistral-Small | Open-source | Free | κ = ??? (ready to run) |

## Expected Timeline

- **Mistral coding**: ~30-40 minutes (999 calls)
- Runs independently of Gemini
- Can run in parallel or after Gemini completes

## Processing & Analysis

Once both complete, I'll:
1. Process all responses to CSV
2. Calculate Cohen's Kappa for each model
3. Create comparative visualizations
4. Generate final report with all three models

## Ready When You Are!

Just provide your HuggingFace token and I'll start the Mistral run immediately.
