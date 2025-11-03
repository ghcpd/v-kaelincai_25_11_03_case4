# PowerShell Setup Script for Project B - Refactored Implementation

Write-Host "=" -NoNewline; Write-Host ("=" * 79)
Write-Host "Setting up Project B - Refactored Implementation"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..."
python -m pip install --upgrade pip
pip install -r requirements_optimized.txt

# Create necessary directories
Write-Host "`nCreating directories..."
New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "performance" | Out-Null

# Copy shared test data
Write-Host "`nCopying shared test data..."
$sharedData = Join-Path $PSScriptRoot "..\shared_data\test_data.json"
$targetData = Join-Path $PSScriptRoot "data\test_data.json"
if (Test-Path $sharedData) {
    Copy-Item $sharedData $targetData -Force
    Write-Host "Test data copied successfully"
} else {
    Write-Host "Warning: Shared test data not found at $sharedData"
}

Write-Host "`n" -NoNewline; Write-Host ("=" * 79)
Write-Host "Setup complete for Project B!"
Write-Host "=" -NoNewline; Write-Host ("=" * 79)
