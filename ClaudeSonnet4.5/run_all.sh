#!/bin/bash
# Master Bash Script to Run All Tests and Generate Comparison Report

echo ""
echo "================================================================================"
echo "REFACTORING EVALUATION - AUTOMATED TEST SUITE"
echo "================================================================================"
echo ""

project_a_failed=false
project_b_failed=false

# Step 1: Setup Project A
echo "STEP 1: Setting up Project A (Original Implementation)..."
echo "--------------------------------------------------------------------------------"
cd ProjectA_PreRefactor
bash setup.sh
if [ $? -ne 0 ]; then
    echo "Warning: Project A setup encountered issues"
fi
cd ..
echo ""

# Step 2: Setup Project B
echo "STEP 2: Setting up Project B (Refactored Implementation)..."
echo "--------------------------------------------------------------------------------"
cd ProjectB_PostRefactor
bash setup_optimized.sh
if [ $? -ne 0 ]; then
    echo "Warning: Project B setup encountered issues"
fi
cd ..
echo ""

# Step 3: Run Project A Tests
echo "STEP 3: Running tests for Project A (Original Implementation)..."
echo "--------------------------------------------------------------------------------"
cd ProjectA_PreRefactor
bash run_tests.sh
if [ $? -ne 0 ]; then
    project_a_failed=true
    echo "Project A tests completed with failures"
else
    echo "Project A tests completed successfully"
fi
cd ..
echo ""

# Step 4: Run Project B Tests
echo "STEP 4: Running tests for Project B (Refactored Implementation)..."
echo "--------------------------------------------------------------------------------"
cd ProjectB_PostRefactor
bash run_tests.sh
if [ $? -ne 0 ]; then
    project_b_failed=true
    echo "Project B tests completed with failures"
else
    echo "Project B tests completed successfully"
fi
cd ..
echo ""

# Step 5: Generate Comparison Report
echo "STEP 5: Generating comparison report..."
echo "--------------------------------------------------------------------------------"
python3 generate_comparison.py 2>/dev/null || python generate_comparison.py
echo ""

# Final Summary
echo "================================================================================"
echo "EXECUTION SUMMARY"
echo "================================================================================"
echo ""

if [ "$project_a_failed" = true ]; then
    echo "Project A (Original):     FAILED"
else
    echo "Project A (Original):     PASSED"
fi

if [ "$project_b_failed" = true ]; then
    echo "Project B (Refactored):   FAILED"
else
    echo "Project B (Refactored):   PASSED"
fi

echo ""
echo "Generated Files:"
echo "  - compare_report.md          (Detailed comparison report)"
echo "  - comparison_summary.json    (Metrics summary)"
echo ""
echo "Individual Test Results:"
echo "  Project A:"
echo "    - ProjectA_PreRefactor/logs/test_log_original.txt"
echo "    - ProjectA_PreRefactor/performance/metrics_original.json"
echo "  Project B:"
echo "    - ProjectB_PostRefactor/logs/test_log_refactored.txt"
echo "    - ProjectB_PostRefactor/performance/metrics_refactored.json"
echo ""
echo "================================================================================"

# Exit with error if any project failed
if [ "$project_a_failed" = true ] || [ "$project_b_failed" = true ]; then
    echo "Some tests failed. Please review the reports above."
    exit 1
else
    echo "All tests passed successfully!"
    exit 0
fi
