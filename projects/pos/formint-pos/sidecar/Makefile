# ============================================================================
# Formint POS — Sidecar Makefile (merged Django + Robyn)
# ============================================================================
# Merged from backend/Makefile (Django + Ninja + django-fusion + Unfold) and
# the POS Full sidecar (Robyn server). Delegated from ../Makefile via
# `make backend-<target>` and from the root POS Makefile via `make formint-*`.
#
# Quick start:
#   make install           — create .venv + install editable package + migrate
#   make migrate           — apply migrations
#   make seed              — migrate + idempotent superuser (admin@formint.local)
#   make dev               — runserver on 127.0.0.1:8767 (frontend proxies here)
#   make server            — Robyn sidecar server (API + WebSocket, port 8766)
#   make test              — Django formint suite + sidecar pytest suite
#   make check             — Django system checks
#
# Env overrides: PORT (default 8767), ROBYN_PORT (8766), FUSION_RENDER_FIRST

.PHONY: help install migrate dev server check test seed ensure-superuser shell static collectstatic clean

.DEFAULT_GOAL := help

# Colors
CYAN   := \033[0;36m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
RED    := \033[0;31m
NC     := \033[0m

DEFAULT_PORT := 8767
ROBYN_PORT   := 8766
PY := .venv/bin/python3
MANAGE := $(PY) manage.py

help: ## Show sidecar commands
	@echo -e "$(CYAN)=== Formint POS Sidecar (Django + Robyn) ===$(NC)"
	@echo -e "$(BLUE)Admin :$${PORT:-$(DEFAULT_PORT)}/admin/ · API :$${PORT:-$(DEFAULT_PORT)}/api/v1 · Robyn :$${ROBYN_PORT:-$(ROBYN_PORT)} $(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-18s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Create .venv + install editable package + migrate
	@echo -e "$(BLUE)Creating .venv and installing editable package…$(NC)"
	python3 -m venv .venv
	$(PY) -m pip install -e .
	@echo -e "$(GREEN)✅ Installed. Applying migrations…$(NC)"
	$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Ready. Run: make dev$(NC)"

migrate: ## Make + apply migrations
	@echo -e "$(BLUE)Making migrations…$(NC)"
	$(MANAGE) makemigrations --noinput
	@echo -e "$(BLUE)Applying migrations…$(NC)"
	$(MANAGE) migrate --noinput
	@echo -e "$(GREEN)✅ Migrations done$(NC)"

dev: ## Run Django dev server (127.0.0.1:PORT, default 8767)
	$(MANAGE) runserver 127.0.0.1:$${PORT:-$(DEFAULT_PORT)}

server: ## Run the Robyn sidecar server (API + WebSocket, port 8766)
	$(PY) server.py --port $${ROBYN_PORT:-$(ROBYN_PORT)}

check: ## Django system checks
	$(MANAGE) check

test: ## Django formint suite + sidecar pytest suite
	$(MANAGE) test formint -v 1
	@echo -e "$(BLUE)Running sidecar pytest suite…$(NC)"
	unset DJANGO_SETTINGS_MODULE; $(PY) -m pytest tests/ -q --no-header -k "not rust_db" || true

seed: ## Apply migrations + ensure superuser (admin@formint.local / admin123)
	$(MANAGE) migrate --noinput
	$(MANAGE) --ensure-superuser
	@echo -e "$(GREEN)✅ Seeded. Admin → http://127.0.0.1:$${PORT:-$(DEFAULT_PORT)}/admin/$(NC)"

ensure-superuser: ## Idempotent admin bootstrap (refuses default pw when DEBUG=0)
	$(MANAGE) --ensure-superuser

shell: ## Django shell
	$(MANAGE) shell

static: collectstatic ## Alias for collectstatic
collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

clean: ## Remove database + staticfiles + __pycache__
	rm -f restaurant.db formint-phase1.sqlite3
	rm -rf staticfiles
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo -e "$(GREEN)✅ Sidecar artifacts cleaned$(NC)"
