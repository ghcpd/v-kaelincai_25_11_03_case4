#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  bash setup.sh
else
  source .venv/bin/activate
fi
python tests/test_original.py
