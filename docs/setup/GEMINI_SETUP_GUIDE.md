# Gemini Analysis Setup Guide

This guide explains how to run the qualitative coding analysis using Google's Gemini API instead of OpenAI's GPT.

## What's Been Prepared

I've created a complete workflow to replicate the original analysis using Gemini:

### Scripts Created

1. **`src/collection/gemini_coding_workflow.py`** - Main coding script
   - Makes Gemini API calls to code passages
   - Supports all 4 experimental conditions:
     - Per-code with justification
     - Per-code without justification
     - Full codebook with justification
     - Full codebook without justification
   - Saves raw responses in same format as original

2. **`src/processing/process_gemini_results.py`** - Processing script
   - Converts raw Gemini responses into tabular format
   - Extracts code applications from each response
   - Creates processed_responses.csv files

3. **`src/analysis/analyze_gemini_results.py`** - Analysis script
   - Calculates intercoder reliability metrics (Cohen's Kappa, etc.)
   - Compares Gemini vs gold standard
   - Compares Gemini vs GPT performance

4. **`src/visualization/create_gemini_visualizations.R`** - Visualization script
   - Creates 4 comparison plots
   - Shows Gemini vs GPT performance
   - Highlights differences by code

5. **`src/collection/run_gemini_analysis.py`** - Master script
   - Runs entire workflow automatically
   - Handles errors and progress reporting

### Package Installation

The required `google-generativeai` package has been installed.

## How to Run

### Option 1: Simple (Recommended)

Just run the master script with your API key:

```bash
cd "/path/to/repo"
python src/collection/run_gemini_analysis.py YOUR_GEMINI_API_KEY
```

This will automatically:
1. Make all Gemini API calls (~444 calls total)
2. Process the responses
3. Calculate metrics
4. Create visualizations
5. Generate comparison report

### Option 2: Step by Step

If you prefer to run steps individually:

```python
# Run from the repository root
import sys
sys.path.extend(["src/collection", "src/processing", "src/analysis"])

# Step 1: Run Gemini coding
from gemini_coding_workflow import main, initialize_gemini
initialize_gemini('YOUR_API_KEY')
paths = main('YOUR_API_KEY')

# Step 2: Process responses
from process_gemini_results import process_all_gemini_outputs
process_all_gemini_outputs()

# Step 3: Analyze results
from analyze_gemini_results import main as analyze_main
results = analyze_main()

# Step 4: Create visualizations (run in a shell)
# Rscript src/visualization/create_gemini_visualizations.R
```

### Option 3: Custom Conditions

To run only specific conditions:

```python
import sys
sys.path.append("src/collection")

from gemini_coding_workflow import main

# Only per-code approach
main('YOUR_API_KEY', conditions_to_run='per-code-only')

# Only full codebook approach
main('YOUR_API_KEY', conditions_to_run='full-only')
```

## Expected Costs & Time

### API Costs (Estimated)
- **Total API calls**: ~444 calls (111 passages × 4 conditions)
  - Per-code with justification: 111 passages × 9 codes = 999 calls
  - Per-code without justification: 111 passages × 9 codes = 999 calls
  - Full codebook with justification: 111 passages
  - Full codebook without justification: 111 passages
  - **Total**: 2,220 calls

- **Gemini 1.5 Pro pricing** (as of late 2024):
  - Input: ~$0.00125 per 1K characters
  - Output: ~$0.005 per 1K characters
  - **Estimated total cost**: $5-15 depending on response lengths

### Time Required
- **API calls**: 30-60 minutes (with rate limiting)
- **Processing**: 1-2 minutes
- **Analysis**: 1-2 minutes
- **Visualizations**: < 1 minute
- **Total**: ~45-75 minutes

## Output Structure

After running, you'll have:

```
results/raw/output_gemini/
├── per-code-with-justification_t=0_top_p=1_model=gemini/
│   ├── scholar/
│   │   ├── message_9.txt
│   │   ├── message_10.txt
│   │   └── ...
│   ├── activist/
│   ├── ... (all 9 codes)
│   ├── processed_responses.csv
│   └── detailed_report.csv
├── per-code-without-justification_t=0_top_p=1_model=gemini/
├── full-codebook-with-justification_t=0_top_p=1_model=gemini/
└── full-codebook-without-justification_t=0_top_p=1_model=gemini/

results/outputs/
├── gemini_vs_gpt_comparison.csv          # Main comparison results
results/figures/
├── gemini_comparison_by_code.png         # Bar chart by code
├── gemini_average_comparison.png         # Average performance
├── gemini_gpt4_difference.png            # Difference plot
└── gemini_gpt4_heatmap.png              # Heatmap comparison
```

## What Happens Next

Once you provide your API key and I run the analysis, we'll be able to answer:

1. **How does Gemini compare to GPT-4?**
   - Which model has higher intercoder reliability?
   - Which codes does each model handle best?
   - Does chain-of-thought help Gemini as much as GPT?

2. **Is Gemini suitable for qualitative coding?**
   - Does it achieve "substantial agreement" (κ > 0.60)?
   - Which experimental conditions work best?
   - Are there particular codes where Gemini excels/struggles?

3. **What are the practical implications?**
   - Cost comparison (Gemini vs GPT)
   - Speed comparison
   - Ease of use
   - API reliability

## Troubleshooting

### API Key Issues
- Make sure your Gemini API key is active
- Check you have billing enabled on Google AI Studio
- Verify you haven't exceeded rate limits

### Rate Limiting
- The script includes automatic retry with exponential backoff
- Rate limits: 60 requests per minute (default)
- If you hit limits, the script will wait and retry

### Processing Errors
- If processing fails, check that all message_*.txt files were created
- Verify the format matches expected pattern
- Try running `src/processing/process_gemini_results.py` separately

## Ready to Go!

Everything is set up and ready. Just provide your Gemini API key and I'll run the complete analysis!

The code is modular and well-documented, so you can:
- Modify prompts if needed
- Add additional experimental conditions
- Adjust temperature/top_p parameters
- Export results in different formats

Let me know when you'd like to proceed!
