#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

bash "$ROOT/project_a/run_tests.sh"
bash "$ROOT/project_b/run_tests.sh"
python "$ROOT/scripts/generate_report.py"

echo "Combined comparison report written to $ROOT/compare_report.md"
