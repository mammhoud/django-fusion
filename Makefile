.PHONY: help check validate-config build-assets test compose assets website-ctc website-structa tests tests-website run-dev migrations migrate

PYTHON ?= .venv/bin/python
MANAGE ?= $(PYTHON) manage.py

help:
	@echo "Top-level targets:"
	@echo "  compose        - Delegate to compose/Makefile"
	@echo "  assets         - Delegate to assets/Makefile"
	@echo "  website-ctc    - Delegate to ctc-research.com/Makefile"
	@echo "  website-structa- Delegate to structa.cloud/Makefile"
	@echo "  check          - Django checks"
	@echo "  test           - Pytest"
	@echo "  tests-website  - Run tests for WEBSITE=ctc|structa|all"

compose:
	$(MAKE) -C compose $(filter-out $@,$(MAKECMDGOALS))

assets:
	$(MAKE) -C assets $(filter-out $@,$(MAKECMDGOALS))

website-ctc:
	$(MAKE) -C ctc-research.com $(filter-out $@,$(MAKECMDGOALS))

website-structa:
	$(MAKE) -C structa.cloud $(filter-out $@,$(MAKECMDGOALS))

check:
	$(MANAGE) check

validate-config:
	@if $(MANAGE) help | grep -q "validate_config"; then $(MANAGE) validate_config; else echo "validate_config command not found"; fi

build-assets:
	$(MAKE) -C assets build

test:
	$(PYTHON) -m pytest

run-dev:
	$(MANAGE) runserver 0.0.0.0:8000

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate


tests:
	$(MAKE) -C tests $(filter-out $@,$(MAKECMDGOALS))

.PHONY: tests-unit tests-integration tests-websites
tests-unit:
	$(MAKE) -C tests unit
tests-integration:
	$(MAKE) -C tests integration
tests-websites:
	$(MAKE) -C tests websites


tests-website:
	./scripts/run_website_tests.sh $${WEBSITE:-all}
