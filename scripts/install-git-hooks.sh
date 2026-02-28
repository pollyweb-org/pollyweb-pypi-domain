#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

chmod +x .githooks/pre-push
chmod +x scripts/check-security.sh

git config core.hooksPath .githooks

echo "Git hooks path configured to: $(git config --get core.hooksPath)"
echo "pre-push hook is active. Pushes will be blocked if tests or security checks fail."
