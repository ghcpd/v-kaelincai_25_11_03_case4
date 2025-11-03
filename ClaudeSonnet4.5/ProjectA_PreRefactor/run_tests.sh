#!/bin/bash
# Run tests for Original Implementation (Pre-Refactor)

echo "======================================================================"
echo "Running Tests for Project A - Original Implementation"
echo "======================================================================"

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Run tests
python tests/test_original.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "======================================================================"
echo "Test execution completed for Original Implementation"
echo "Exit Code: $EXIT_CODE"
echo "======================================================================"
echo "Results saved to:"
echo "  - logs/test_log_original.txt"
echo "  - performance/metrics_original.json"
echo "======================================================================"

exit $EXIT_CODE
