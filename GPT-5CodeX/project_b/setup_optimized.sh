#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

if [[ "${OS-}" == "Windows_NT" ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

python -m pip install --upgrade pip > /dev/null
if [ -s requirements_optimized.txt ]; then
  python -m pip install -r requirements_optimized.txt
fi

echo "Environment ready for Project B."
