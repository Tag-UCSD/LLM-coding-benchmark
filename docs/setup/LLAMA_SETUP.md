# Llama 3.1 70B Coding Setup (via Groq)

## Why Groq Instead of HuggingFace?

HuggingFace's free Inference API doesn't provide access to large language models like Mistral-Small or Llama.

**Groq** offers a better solution:
- ✅ **FREE** API access to Llama 3.1 70B
- ✅ **Extremely fast** inference (fastest in the industry)
- ✅ High quality results comparable to GPT-4
- ✅ Generous free tier limits
- ✅ Simple API (similar to OpenAI)

## Quick Start

1. **Get a FREE Groq API Key**:
   - Go to: https://console.groq.com
   - Sign up (free, no credit card required)
   - Navigate to API Keys section
   - Click "Create API Key"
   - Copy the key (starts with `gsk_...`)

2. **Run the Llama coding**:
   ```bash
   cd "/path/to/repo"
   python -c "
   import sys
   sys.path.append("src/collection")
   from groq_coding_workflow import run_per_code_llama
   run_per_code_llama('YOUR_GROQ_API_KEY_HERE')
   "
   ```

## What This Does

- Uses **Llama 3.1 70B Versatile** (open-source)
- Runs the **per-code with justification** approach
- Makes ~999 API calls (same as Gemini and GPT-4)
- **FREE** with Groq API key
- **FAST** - Groq has the fastest inference in the industry
- Results comparable to GPT-4 and Gemini

## Three-Way Comparison

After all models complete, you'll have:

| Model | Type | Cost | Performance |
|-------|------|------|-------------|
| GPT-4 | Proprietary | ~$15-20 | κ = 0.676 (baseline) |
| Gemini 2.5 Flash-Lite | Proprietary | Free tier | κ = ??? (running) |
| Llama 3.1 70B | Open-source | Free | κ = ??? (ready to run) |

## Expected Timeline

- **Llama coding**: ~10-15 minutes (999 calls)
- Groq is **extremely fast** - much faster than Gemini or GPT
- Runs independently of Gemini
- Can run in parallel while Gemini completes

## Model Details

**Llama 3.1 70B Versatile**:
- 70 billion parameters
- Open-source (Meta)
- State-of-the-art performance
- Excellent for instruction following
- Comparable to GPT-4 on many benchmarks

## Processing & Analysis

Once all three models complete, the analysis will:
1. Process all responses to CSV
2. Calculate Cohen's Kappa for each model
3. Create three-way comparative visualizations
4. Generate final report comparing all models

## Ready When You Are!

Just provide your Groq API key and the Llama run will start immediately.

**Get your free key at**: https://console.groq.com
