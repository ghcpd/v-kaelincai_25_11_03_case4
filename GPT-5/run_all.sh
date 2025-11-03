#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(dirname "$0")"
cd "$ROOT_DIR"

# Run Project A
bash ProjectA/run_tests.sh || echo "Project A tests encountered errors"
# Run Project B
bash ProjectB/run_tests.sh || echo "Project B tests encountered errors"

python run_all.py

echo "Comparison report generated at compare_report.md"
