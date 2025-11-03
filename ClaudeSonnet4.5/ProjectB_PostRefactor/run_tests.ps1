# PowerShell Test Runner for Project B - Refactored Implementation

Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "Running Tests for Project B - Refactored Implementation"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Run tests
python tests\test_refactored.py

# Capture exit code
$exitCode = $LASTEXITCODE

Write-Host "`n" -NoNewline; Write-Host ("=" * 79)
Write-Host "Test execution completed for Refactored Implementation"
Write-Host "Exit Code: $exitCode"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "Results saved to:"
Write-Host "  - logs\test_log_refactored.txt"
Write-Host "  - performance\metrics_refactored.json"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

exit $exitCode
