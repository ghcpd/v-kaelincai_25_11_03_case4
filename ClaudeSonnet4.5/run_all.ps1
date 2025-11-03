# Master PowerShell Script to Run All Tests and Generate Comparison Report

Write-Host "`n"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "REFACTORING EVALUATION - AUTOMATED TEST SUITE"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "`n"

$ErrorActionPreference = "Continue"
$projectAFailed = $false
$projectBFailed = $false

# Step 1: Setup Project A
Write-Host "STEP 1: Setting up Project A (Original Implementation)..."
Write-Host "-" -NoNewline; Write-Host ("-" * 79)
Push-Location ProjectA_PreRefactor
& .\setup.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Project A setup encountered issues" -ForegroundColor Yellow
}
Pop-Location
Write-Host "`n"

# Step 2: Setup Project B
Write-Host "STEP 2: Setting up Project B (Refactored Implementation)..."
Write-Host "-" -NoNewline; Write-Host ("-" * 79)
Push-Location ProjectB_PostRefactor
& .\setup_optimized.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Project B setup encountered issues" -ForegroundColor Yellow
}
Pop-Location
Write-Host "`n"

# Step 3: Run Project A Tests
Write-Host "STEP 3: Running tests for Project A (Original Implementation)..."
Write-Host "-" -NoNewline; Write-Host ("-" * 79)
Push-Location ProjectA_PreRefactor
& .\run_tests.ps1
if ($LASTEXITCODE -ne 0) {
    $projectAFailed = $true
    Write-Host "Project A tests completed with failures" -ForegroundColor Yellow
} else {
    Write-Host "Project A tests completed successfully" -ForegroundColor Green
}
Pop-Location
Write-Host "`n"

# Step 4: Run Project B Tests
Write-Host "STEP 4: Running tests for Project B (Refactored Implementation)..."
Write-Host "-" -NoNewline; Write-Host ("-" * 79)
Push-Location ProjectB_PostRefactor
& .\run_tests.ps1
if ($LASTEXITCODE -ne 0) {
    $projectBFailed = $true
    Write-Host "Project B tests completed with failures" -ForegroundColor Yellow
} else {
    Write-Host "Project B tests completed successfully" -ForegroundColor Green
}
Pop-Location
Write-Host "`n"

# Step 5: Generate Comparison Report
Write-Host "STEP 5: Generating comparison report..."
Write-Host "-" -NoNewline; Write-Host ("-" * 79)
python generate_comparison.py
Write-Host "`n"

# Final Summary
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "EXECUTION SUMMARY"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host ""

if ($projectAFailed) {
    Write-Host "Project A (Original):     FAILED" -ForegroundColor Red
} else {
    Write-Host "Project A (Original):     PASSED" -ForegroundColor Green
}

if ($projectBFailed) {
    Write-Host "Project B (Refactored):   FAILED" -ForegroundColor Red
} else {
    Write-Host "Project B (Refactored):   PASSED" -ForegroundColor Green
}

Write-Host ""
Write-Host "Generated Files:"
Write-Host "  - compare_report.md          (Detailed comparison report)"
Write-Host "  - comparison_summary.json    (Metrics summary)"
Write-Host ""
Write-Host "Individual Test Results:"
Write-Host "  Project A:"
Write-Host "    - ProjectA_PreRefactor\logs\test_log_original.txt"
Write-Host "    - ProjectA_PreRefactor\performance\metrics_original.json"
Write-Host "  Project B:"
Write-Host "    - ProjectB_PostRefactor\logs\test_log_refactored.txt"
Write-Host "    - ProjectB_PostRefactor\performance\metrics_refactored.json"
Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

# Exit with error if any project failed
if ($projectAFailed -or $projectBFailed) {
    Write-Host "Some tests failed. Please review the reports above." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    exit 0
}
