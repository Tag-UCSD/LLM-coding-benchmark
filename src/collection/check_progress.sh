#!/bin/bash
# Progress checker for Gemini coding

echo "================================================================================  "
echo "GEMINI CODING PROGRESS"
echo "================================================================================"
echo ""

# Count files in each condition
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

for dir in "$REPO_ROOT/results/raw/output_gemini"/*/; do
    if [ -d "$dir" ]; then
        condition=$(basename "$dir")
        count=$(find "$dir" -name "message_*.txt" 2>/dev/null | wc -l | tr -d ' ')

        # Expected counts per condition
        if [[ $condition == *"per-code"* ]]; then
            expected=999
        else
            expected=111
        fi

        pct=$((count * 100 / expected))
        echo "$condition"
        echo "  Progress: $count/$expected calls ($pct%)"
        echo ""
    fi
done

echo "================================================================================"
