.PHONY: help check validate-config build-assets test audit-config

PYTHON ?= .venv/bin/python
MANAGE ?= $(PYTHON) manage.py

help:
	@echo "Available targets:"
	@echo "  check            - Run Django system checks"
	@echo "  validate-config  - Validate env/yml config overlap"
	@echo "  build-assets     - Run Django build_assets command"
	@echo "  test             - Run pytest suite"

check:
	$(MANAGE) check

validate-config:
	@if $(MANAGE) help | grep -q "validate_config"; then \
		$(MANAGE) validate_config; \
	else \
		echo "validate_config command is not registered in current settings profile"; \
	fi

build-assets:
	@if $(MANAGE) help | grep -q "build_assets"; then \
		$(MANAGE) build_assets --no-input; \
	else \
		echo "build_assets command is not registered in current settings profile"; \
	fi

test:
	$(PYTHON) -m pytest


audit-config:
	@echo "Checking config/static/template paths..."
	@test -d configs/settings/ENV
	@test -d assets/static
	@test -d templates
	@test -d plugins/templates
	@test -d www/core/templates
	@echo "OK: core config and template/static directories exist"
