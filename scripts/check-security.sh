#!/usr/bin/env bash
set -euo pipefail

echo "[security] Running dependency vulnerability scan..."

if [ -x ".venv/bin/python" ]; then
  AUDIT_CMD=(.venv/bin/python -m pip_audit)
elif command -v pip-audit >/dev/null 2>&1; then
  AUDIT_CMD=(pip-audit)
else
  echo "[security] pip-audit is not installed and .venv is unavailable." >&2
  echo "[security] Install pip-audit before pushing." >&2
  exit 1
fi

"${AUDIT_CMD[@]}"

echo "[security] No known dependency vulnerabilities found."
