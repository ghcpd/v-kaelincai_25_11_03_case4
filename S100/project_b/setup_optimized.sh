#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
python -m venv "$PROJECT_ROOT/.venv_post"
if [ -d "$PROJECT_ROOT/.venv_post/Scripts" ]; then
  source "$PROJECT_ROOT/.venv_post/Scripts/activate"
else
  source "$PROJECT_ROOT/.venv_post/bin/activate"
fi
pip install --upgrade pip
pip install -r "$PROJECT_ROOT/requirements_optimized.txt"
echo "Environment ready for Project B"
