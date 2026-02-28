SHELL := /bin/bash

.PHONY: install-hooks test security

install-hooks:
	./scripts/install-git-hooks.sh

test:
	@if [ -d "__dumps__/DOMAIN" ]; then \
		backup_dir="__dumps__/DOMAIN.make.$$(date +%s)"; \
		echo "Rotating prior test dump to $$backup_dir"; \
		mv "__dumps__/DOMAIN" "$$backup_dir"; \
	fi
	@if [ -x .venv/bin/python ]; then \
		./.venv/bin/python -m pytest -q; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest -q; \
	else \
		echo "pytest is not installed and .venv is unavailable."; \
		exit 1; \
	fi

security:
	@./scripts/check-security.sh
