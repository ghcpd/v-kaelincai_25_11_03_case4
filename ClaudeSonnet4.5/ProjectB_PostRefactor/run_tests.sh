#!/bin/bash
# Run tests for Refactored Implementation (Post-Refactor)

echo "======================================================================"
echo "Running Tests for Project B - Refactored Implementation"
echo "======================================================================"

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Run tests
python tests/test_refactored.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "======================================================================"
echo "Test execution completed for Refactored Implementation"
echo "Exit Code: $EXIT_CODE"
echo "======================================================================"
echo "Results saved to:"
echo "  - logs/test_log_refactored.txt"
echo "  - performance/metrics_refactored.json"
echo "======================================================================"

exit $EXIT_CODE
