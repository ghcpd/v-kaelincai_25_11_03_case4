#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ ! -d "$PROJECT_ROOT/.venv_post" ]; then
  bash "$PROJECT_ROOT/setup_optimized.sh"
fi
if [ -d "$PROJECT_ROOT/.venv_post/Scripts" ]; then
  source "$PROJECT_ROOT/.venv_post/Scripts/activate"
else
  source "$PROJECT_ROOT/.venv_post/bin/activate"
fi
pytest "$PROJECT_ROOT/tests" --disable-warnings --maxfail=1 -q

printf '\nLatest log snapshot (Project B):\n'
cat "$PROJECT_ROOT/logs/log_refactored.txt" 2>/dev/null || true
printf '\nPerformance snapshot (Project B):\n'
cat "$PROJECT_ROOT/performance/time_refactored.txt" 2>/dev/null || true
