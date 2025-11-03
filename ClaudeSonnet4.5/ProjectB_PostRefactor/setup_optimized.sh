#!/bin/bash
# Setup script for Refactored Implementation (Post-Refactor)

echo "Setting up Project B - Refactored Implementation..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_optimized.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p data
mkdir -p logs
mkdir -p performance

echo "Setup complete for Project B!"
echo "To activate the environment, run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
