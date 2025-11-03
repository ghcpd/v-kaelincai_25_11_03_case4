#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ ! -d "$PROJECT_ROOT/.venv_pre" ]; then
  bash "$PROJECT_ROOT/setup.sh"
fi
if [ -d "$PROJECT_ROOT/.venv_pre/Scripts" ]; then
  source "$PROJECT_ROOT/.venv_pre/Scripts/activate"
else
  source "$PROJECT_ROOT/.venv_pre/bin/activate"
fi
pytest "$PROJECT_ROOT/tests" --disable-warnings --maxfail=1 -q

printf '\nLatest log snapshot (Project A):\n'
cat "$PROJECT_ROOT/logs/log_original.txt" 2>/dev/null || true
printf '\nPerformance snapshot (Project A):\n'
cat "$PROJECT_ROOT/performance/time_original.txt" 2>/dev/null || true
