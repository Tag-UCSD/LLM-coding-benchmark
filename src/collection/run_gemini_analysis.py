#!/usr/bin/env python3
"""
Master script to run complete Gemini analysis workflow

Usage:
    python run_gemini_analysis.py YOUR_API_KEY

This will:
1. Run Gemini coding on all conditions (per-code and full codebook, with/without justification)
2. Process the raw responses into tabular format
3. Calculate intercoder reliability metrics
4. Compare Gemini vs GPT performance
5. Generate visualizations

Estimated time: 30-60 minutes depending on API rate limits
Estimated cost: ~$5-10 depending on Gemini API pricing
"""

import sys
import os
import subprocess

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")


def run_step(step_num, step_name, func, *args, **kwargs):
    """Run a step in the workflow with error handling."""
    print_header(f"STEP {step_num}: {step_name}")
    try:
        result = func(*args, **kwargs)
        print(f"\n✓ Step {step_num} completed successfully!")
        return result
    except Exception as e:
        print(f"\n✗ Step {step_num} failed: {str(e)}")
        raise


def main(api_key=None, skip_coding=False):
    """
    Run the complete Gemini analysis workflow.

    Args:
        api_key: Gemini API key (required unless skip_coding=True)
        skip_coding: If True, skip API calls and only process existing outputs
    """

    print_header("GEMINI QUALITATIVE CODING - COMPLETE WORKFLOW")

    if api_key is None and not skip_coding:
        print("ERROR: API key required!")
        print("\nUsage:")
        print("  python run_gemini_analysis.py YOUR_API_KEY")
        print("\nOr to skip coding and only process existing results:")
        print("  python run_gemini_analysis.py --skip-coding")
        sys.exit(1)

    # Change to repository root
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(repo_root)

    # Ensure local modules are importable
    src_dir = os.path.join(repo_root, "src")
    for subdir in ("collection", "processing", "analysis"):
        sys.path.insert(0, os.path.join(src_dir, subdir))

    # Step 1: Run Gemini coding (if not skipped)
    if not skip_coding:
        def run_gemini_coding():
            from gemini_coding_workflow import main as gemini_main
            return gemini_main(api_key, conditions_to_run='all')

        paths = run_step(1, "Run Gemini API Coding", run_gemini_coding)
        print(f"\nGenerated outputs in {len(paths)} condition directories")
    else:
        print_header("STEP 1: SKIPPED (using existing outputs)")

    # Step 2: Process Gemini responses
    def process_responses():
        from process_gemini_results import process_all_gemini_outputs
        process_all_gemini_outputs()

    run_step(2, "Process Gemini Responses", process_responses)

    # Step 3: Analyze results
    def analyze_results():
        from analyze_gemini_results import main as analyze_main
        return analyze_main()

    comparison_df = run_step(3, "Calculate Intercoder Reliability", analyze_results)

    # Step 4: Create visualizations
    def create_visualizations():
        print("Creating R visualizations...")
        result = subprocess.run(
            ["Rscript", "src/visualization/create_gemini_visualizations.R"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("R output:", result.stdout)
            print("R errors:", result.stderr)
            raise Exception("R visualization failed")
        print(result.stdout)

    # Check if R visualization script exists
    if os.path.exists("create_gemini_visualizations.R"):
        run_step(4, "Create Visualizations", create_visualizations)
    else:
        print_header("STEP 4: Create Visualizations (SKIPPED - script not yet created)")

    # Final summary
    print_header("WORKFLOW COMPLETE!")

    print("Summary of outputs:")
    print("  📁 results/raw/output_gemini/   - Raw Gemini responses")
    print("  📁 results/outputs/             - Analysis results tables")
    print("  📁 results/figures/             - Visualizations")
    print("  📊 results/outputs/gemini_vs_gpt_comparison.csv - Performance comparison")
    print("\nNext steps:")
    print("  1. Review the comparison results in results/outputs/gemini_vs_gpt_comparison.csv")
    print("  2. Check visualizations in results/figures/")
    print("  3. Compare detailed reports in each results/raw/output_gemini/*/ directory")

    return comparison_df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "=" * 80)
        print("Gemini Qualitative Coding - Complete Workflow".center(80))
        print("=" * 80)
        print("\nThis script requires a Gemini API key.")
        print("\nUsage:")
        print("  python run_gemini_analysis.py YOUR_API_KEY")
        print("\nOr to process existing outputs without making new API calls:")
        print("  python run_gemini_analysis.py --skip-coding")
        print("\n" + "=" * 80)
        sys.exit(1)

    if sys.argv[1] == "--skip-coding":
        main(skip_coding=True)
    else:
        api_key = sys.argv[1]
        main(api_key)
