#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

rm -rf dist build

if [ -x ".venv/bin/python" ]; then
  PYTHON=(.venv/bin/python)
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=(python3)
else
  echo "python3 not found." >&2
  exit 1
fi

"${PYTHON[@]}" -m pip install -U build twine
"${PYTHON[@]}" -m build
"${PYTHON[@]}" -m twine upload dist/*
