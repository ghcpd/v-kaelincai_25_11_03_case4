#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pushd "$ROOT_DIR/project_a" > /dev/null
./setup.sh
./run_tests.sh
popd > /dev/null

pushd "$ROOT_DIR/project_b" > /dev/null
./setup_optimized.sh
./run_tests.sh
popd > /dev/null

python "$ROOT_DIR/tools/generate_compare_report.py"

echo "Full comparison workflow complete. Report available at $ROOT_DIR/compare_report.md"
