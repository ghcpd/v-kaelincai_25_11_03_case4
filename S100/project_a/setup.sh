#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
python -m venv "$PROJECT_ROOT/.venv_pre"
if [ -d "$PROJECT_ROOT/.venv_pre/Scripts" ]; then
  source "$PROJECT_ROOT/.venv_pre/Scripts/activate"
else
  source "$PROJECT_ROOT/.venv_pre/bin/activate"
fi
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements.txt"
echo "Environment ready for Project A"
