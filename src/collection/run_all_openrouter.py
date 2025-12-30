"""
Unified runner for collecting data from all models via OpenRouter
With automatic rate limit handling and progress tracking
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from unified_openrouter_workflow import run_per_code_openrouter, MODELS

def run_all_models(api_key, models_to_run=['qwen', 'llama', 'gemini']):
    """
    Run data collection for all specified models.

    Args:
        api_key: OpenRouter API key
        models_to_run: List of model names to run (default: all)
    """

    print("=" * 80)
    print("RUNNING ALL MODELS VIA OPENROUTER")
    print("=" * 80)
    print(f"Models to process: {', '.join(models_to_run)}")
    print(f"Total API calls per model: ~999 (9 codes × 111 passages)")
    print()

    results = {}

    for model_name in models_to_run:
        if model_name not in MODELS:
            print(f"⚠ Warning: Unknown model '{model_name}', skipping...")
            continue

        model_id = MODELS[model_name]

        print("\n" + "=" * 80)
        print(f"PROCESSING: {model_name.upper()}")
        print(f"Model ID: {model_id}")
        print("=" * 80)

        try:
            path = run_per_code_openrouter(
                api_key=api_key,
                model_name=model_name,
                model_id=model_id,
                with_justification=True
            )
            results[model_name] = {'status': 'success', 'path': path}
            print(f"\n✓ {model_name} completed successfully")

        except KeyboardInterrupt:
            print(f"\n⚠ Interrupted during {model_name}")
            print("Progress has been saved. You can resume later.")
            results[model_name] = {'status': 'interrupted', 'path': None}
            break

        except Exception as e:
            print(f"\n✗ Error with {model_name}: {str(e)}")
            results[model_name] = {'status': 'error', 'error': str(e)}
            # Continue with next model
            continue

    print("\n" + "=" * 80)
    print("COLLECTION SUMMARY")
    print("=" * 80)

    for model_name, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"  ✓ {model_name}: Completed")
        elif status == 'interrupted':
            print(f"  ⚠ {model_name}: Interrupted (can resume)")
        else:
            print(f"  ✗ {model_name}: Failed - {result.get('error', 'Unknown error')}")

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        api_key = sys.argv[1]

        # Allow specifying which models to run
        if len(sys.argv) > 2:
            models = sys.argv[2].split(',')
        else:
            models = ['qwen', 'llama', 'gemini']

        run_all_models(api_key, models)
    else:
        print("\nUsage:")
        print("  python src/collection/run_all_openrouter.py YOUR_API_KEY [models]")
        print("\nExamples:")
        print("  # Run all models:")
        print("  python src/collection/run_all_openrouter.py YOUR_API_KEY")
        print()
        print("  # Run only Qwen:")
        print("  python src/collection/run_all_openrouter.py YOUR_API_KEY qwen")
        print()
        print("  # Run Qwen and Llama:")
        print("  python src/collection/run_all_openrouter.py YOUR_API_KEY qwen,llama")
        print()
        print("Models available: qwen, llama, gemini")
        print()
        print("Note: Llama uses free tier on OpenRouter!")
