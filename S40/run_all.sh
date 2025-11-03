#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$ROOT/ProjectA/run_tests.sh"
bash "$ROOT/ProjectB/run_tests.sh"
python "$ROOT/scripts/generate_report.py"

echo "Comparison report generated at $ROOT/compare_report.md"
