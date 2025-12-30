#!/bin/bash
# Quick one-liner status check
# Usage: ./quick_status.sh

echo "=== Collection Status ==="
echo "Qwen:   $(find results/raw/output_qwen -name 'message_*.txt' 2>/dev/null | wc -l | tr -d ' ')/999"
echo "Llama:  $(find results/raw/output_llama -name 'message_*.txt' 2>/dev/null | wc -l | tr -d ' ')/999"
echo "Gemini: $(find results/raw/output_gemini -name 'message_*.txt' 2>/dev/null | wc -l | tr -d ' ')/999"
echo ""
echo "=== Running Processes ==="
ps aux | grep run_all_openrouter | grep -v grep || echo "None running"
