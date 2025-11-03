# PowerShell Test Runner for Project A - Original Implementation

Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "Running Tests for Project A - Original Implementation"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Run tests
python tests\test_original.py

# Capture exit code
$exitCode = $LASTEXITCODE

Write-Host "`n" -NoNewline; Write-Host ("=" * 79)
Write-Host "Test execution completed for Original Implementation"
Write-Host "Exit Code: $exitCode"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "Results saved to:"
Write-Host "  - logs\test_log_original.txt"
Write-Host "  - performance\metrics_original.json"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

exit $exitCode
