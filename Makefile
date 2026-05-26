
.PHONY: help check validate-config build-assets test audit-config check-sites check-alliance check-paths check-package-installs show-package-sources populate-data run-dev-root run-dev-ctc run-dev-structa

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


check-paths:
	@echo "Validating critical paths..."
	@test -f manage.py
	@test -f ctc-research.com/manage.py
	@test -f structa.cloud/manage.py
	@test -f www/urls.py
	@test -f ctc-research.com/www/urls.py
	@test -f structa.cloud/www/urls.py
	@echo "OK: critical entrypoint paths exist"

check-sites:
	@echo "Running site-level Django checks..."
	@cd ctc-research.com && ../.venv/bin/python manage.py check
	@cd structa.cloud && ../.venv/bin/python manage.py check
	@echo "OK: site-level checks passed"

check-alliance:
	@echo "Checking Alliance scope (structa.cloud plugins import scan)..."
	@rg -n "alliance|django_osoul|django_rseal" structa.cloud/plugins > /dev/null
	@echo "OK: alliance scope imports/config references found"


check-package-installs:
	@echo "Checking internal package imports (django_grep, django_osoul, django_rseal)..."
	@.venv/bin/python -c "import sys,importlib.util as u;mods=['django_grep','django_osoul','django_rseal'];failed=[];[failed.append(m) or print(f'MISSING: {m}') if u.find_spec(m) is None else print(f'OK: {m}') for m in mods];sys.exit(1 if failed else 0)"
	@echo "OK: all internal packages importable"

show-package-sources:
	@echo "Configured GitHub sources (generic branch):"
	@echo "  django-grep  -> https://github.com/mammhoud/django-grep (branch: generic)"
	@echo "  django-osoul -> https://github.com/mammhoud/django-osoul (branch: generic)"
	@echo "  django-rseal -> https://github.com/mammhoud/django-rseal (branch: generic)"


run-dev-root:
	$(PYTHON) manage.py runserver 0.0.0.0:8000

run-dev-ctc:
	@cd ctc-research.com && ../.venv/bin/python manage.py runserver 0.0.0.0:5070

run-dev-structa:
	@cd structa.cloud && ../.venv/bin/python manage.py runserver 0.0.0.0:5071

populate-data:
	$(PYTHON) -m tests.data_populator --site root --verbose
