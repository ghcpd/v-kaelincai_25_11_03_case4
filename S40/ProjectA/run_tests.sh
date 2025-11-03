#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d .venv ]; then
  source .venv/bin/activate
fi

python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

mkdir -p logs performance

python -m pytest tests/test_original.py -q | tee logs/log_original.txt
python -m src.performance_probe --output performance/time_original.json
