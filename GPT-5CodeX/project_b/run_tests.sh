#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Run ./setup_optimized.sh first." >&2
  exit 1
fi

if [[ "${OS-}" == "Windows_NT" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

mkdir -p logs performance
cp -f "$ROOT_DIR/test_data.json" "$SCRIPT_DIR/data/test_data.json"

export PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

python -m tests.runner \
  --implementation-name "Project B - Refactored" \
  --data-file "$SCRIPT_DIR/data/test_data.json" \
  --log-file "$SCRIPT_DIR/logs/log_refactored.txt" \
  --perf-file "$SCRIPT_DIR/performance/time_refactored.txt"

echo "Logs written to $SCRIPT_DIR/logs/log_refactored.txt"
echo "Performance data written to $SCRIPT_DIR/performance/time_refactored.txt"
